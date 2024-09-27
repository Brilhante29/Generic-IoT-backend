from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import paho.mqtt.client as mqtt
import threading
from pymongo import MongoClient
from datetime import datetime, timedelta

app = FastAPI()

# Montar a pasta de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------- Configuração de Templates --------------------
templates = Jinja2Templates(directory="templates")

# -------------------- Configurações de MQTT --------------------
mqtt_broker = "test.mosquitto.org"
mqtt_port = 1883
mqtt_topic_temp = "/ThinkIOT/temp"
mqtt_topic_hum = "/ThinkIOT/hum"
mqtt_topic_cmd = "/ThinkIOT/Subscribe"

# Configuração do cliente MQTT
mqtt_client = mqtt.Client()

# -------------------- Variáveis Globais --------------------
temperature = "N/A"
humidity = "N/A"
led_state = "Desligado"
min_temperature = 22.0  # Valor inicial (padrão)
max_temperature = 27.0  # Valor inicial (padrão)
disable_logic = False  # Desativar a lógica de cena inicialmente

# -------------------- Banco de Dados --------------------
client = MongoClient("mongodb://localhost:27017/")
db = client.iot_data
collection = db.sensor_data

# -------------------- Funções Auxiliares --------------------

# Função para log padronizado
def log_message(level, message):
    print(f"[{level}] {message}")

# Função para validar dados de temperatura e umidade
def is_valid_data(temp, hum):
    try:
        temp = float(temp)
        hum = float(hum)
        return -50 <= temp <= 100 and 0 <= hum <= 100
    except ValueError:
        return False

# Função para salvar dados válidos no MongoDB
def save_to_mongodb(temp, hum):
    if is_valid_data(temp, hum):
        data = {
            "temperature": float(temp),
            "humidity": float(hum),
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(data)
        log_message("LOG", f"Dados salvos no MongoDB: {data}")

# Função para aplicar a lógica de cena com base na temperatura
def apply_scene_logic(temp=None, hum=None):
    global led_state

    log_message("LOG", f"Aplicando lógica de cena. Lógica desativada: {disable_logic}")

    if disable_logic:
        log_message("LOG", "Lógica de cena desativada. Desligando o LED.")
        if led_state == "Ligado":
            mqtt_client.publish(mqtt_topic_cmd, "OFF")
            set_led_state("Desligado", temp if temp is not None else hum)
        return

    try:
        if temp is not None:
            temp = float(temp)
            min_temp = float(min_temperature)
            max_temp = float(max_temperature)

            # Logica para temperatura permanece como estava
            if temp > max_temp:
                log_message("LOG", f"Temperatura ({temp}°C) acima do máximo ({max_temp}°C), desligando o LED.")
                mqtt_client.publish(mqtt_topic_cmd, "OFF")
                set_led_state("Desligado", temp)
            elif temp < min_temp and led_state == "Desligado":
                log_message("LOG", f"Temperatura ({temp}°C) abaixo do mínimo ({min_temp}°C), ligando o LED.")
                mqtt_client.publish(mqtt_topic_cmd, "ON")
                set_led_state("Ligado", temp)

        elif hum is not None:
            hum = float(hum)
            min_hum = float(min_humidity)
            max_hum = float(max_humidity)

            # Lógica para umidade: Ligar o LED se a umidade estiver acima do limite máximo
            if hum > max_hum and led_state == "Desligado":
                log_message("LOG", f"Umidade ({hum}%) acima do máximo ({max_hum}%), ligando o LED.")
                mqtt_client.publish(mqtt_topic_cmd, "ON")
                set_led_state("Ligado", hum)

            # Desligar o LED se a umidade estiver abaixo do limite mínimo
            elif hum < min_hum and led_state == "Ligado":
                log_message("LOG", f"Umidade ({hum}%) abaixo do mínimo ({min_hum}%), desligando o LED.")
                mqtt_client.publish(mqtt_topic_cmd, "OFF")
                set_led_state("Desligado", hum)

    except ValueError as e:
        log_message("ERROR", f"Falha ao converter valores: {e}")


# Função para alterar o estado do LED
def set_led_state(state, temp):
    global led_state
    led_state = state
    log_message("LOG", f"Dispositivo {state}. Temperatura: {temp}°C")

# -------------------- Funções MQTT --------------------

def on_connect(client, userdata, flags, rc):
    log_message("LOG", f"Conectado ao Broker MQTT com resultado {rc}")
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)

def on_message(client, userdata, msg):
    global temperature, humidity
    try:
        if msg.topic == mqtt_topic_temp:
            temperature = float(msg.payload.decode("utf-8"))
            log_message("LOG", f"Nova temperatura recebida: {temperature}°C")
            apply_scene_logic(temperature)

        elif msg.topic == mqtt_topic_hum:
            humidity = float(msg.payload.decode("utf-8"))
            log_message("LOG", f"Nova umidade recebida: {humidity}%")
            save_to_mongodb(temperature, humidity)

    except ValueError:
        log_message("ERROR", f"Não foi possível converter a mensagem: {msg.payload.decode('utf-8')}")
    except Exception as e:
        log_message("ERROR", f"Falha ao processar a mensagem: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# -------------------- Rotas de API --------------------

@app.get("/sistema-antimofo", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/sistema-antimofo/home")

@app.get("/sistema-antimofo/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "temperature": temperature, "humidity": humidity, "led_state": led_state})

@app.get("/sistema-antimofo/monitoramento", response_class=HTMLResponse)
async def monitoramento(request: Request):
    return templates.TemplateResponse("monitoramento.html", {"request": request})

@app.get("/sistema-antimofo/configuracoes", response_class=HTMLResponse)
async def configuracoes(request: Request):
    return templates.TemplateResponse("configuracoes.html", {"request": request})

@app.get("/sistema-antimofo/sobre", response_class=HTMLResponse)
async def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request})

@app.post("/api/toggle-logic")
async def toggle_logic():
    global disable_logic
    disable_logic = not disable_logic
    message = "Lógica de cena desabilitada!" if disable_logic else "Lógica de cena habilitada!"

    if disable_logic and led_state == "Ligado":
        mqtt_client.publish(mqtt_topic_cmd, "OFF")
        set_led_state("Desligado", temperature)
        log_message("LOG", "Lógica desativada e LED desligado.")

    return {"message": message, "disable_logic": disable_logic}

@app.post("/api/configuracao")
async def set_sensor_config(request: Request):
    global min_temperature, max_temperature, min_humidity, max_humidity
    body = await request.json()

    try:
        logic_type = body.get('logicType')

        if logic_type == "temperature":
            min_temperature = float(body['minTemperature'])
            max_temperature = float(body['maxTemperature'])
            log_message("LOG", f"Configurações de temperatura salvas: min_temperature={min_temperature}, max_temperature={max_temperature}")
            return {"message": "Configurações de temperatura salvas com sucesso!"}

        elif logic_type == "humidity":
            min_humidity = float(body['minHumidity'])
            max_humidity = float(body['maxHumidity'])
            log_message("LOG", f"Configurações de umidade salvas: min_humidity={min_humidity}, max_humidity={max_humidity}")
            return {"message": "Configurações de umidade salvas com sucesso!"}

        else:
            return JSONResponse(status_code=400, content={"error": "Tipo de lógica inválido."})

    except (ValueError, KeyError):
        log_message("ERROR", "Valores de configuração inválidos.")
        return JSONResponse(status_code=400, content={"error": "Valores de configuração inválidos."})

@app.get("/api/get-logic-state")
async def get_logic_state():
    return {"disable_logic": disable_logic}

@app.get("/api/led/{state}")
async def control_led(state: str):
    global led_state
    if state == "on":
        mqtt_client.publish(mqtt_topic_cmd, "ON")
        set_led_state("Ligado", temperature)
    elif state == "off":
        mqtt_client.publish(mqtt_topic_cmd, "OFF")
        set_led_state("Desligado", temperature)
    return {"status": f"LED {state}"}

@app.get("/api/dados")
async def get_sensor_data():
    return {"temperature": temperature, "humidity": humidity}

@app.get("/api/dados/{period}")
async def get_sensor_data(period: str):
    periods = {
        "1mes": timedelta(days=30),
        "2semanas": timedelta(weeks=2),
        "1semana": timedelta(weeks=1),
        "3dias": timedelta(days=3)
    }

    if period not in periods:
        return JSONResponse(status_code=400, content={"error": "Período inválido"})

    start_date = datetime.utcnow() - periods[period]
    data_cursor = collection.find({"timestamp": {"$gte": start_date}}).sort("timestamp", 1)
    data = [{"temperature": doc["temperature"], "humidity": doc["humidity"], "led_state": doc.get("led_state", "Desligado"), "timestamp": doc["timestamp"]} for doc in data_cursor]

    return {"data": data}

# -------------------- Inicialização do Servidor --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
