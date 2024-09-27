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
min_temperature = 22.0  # Valor inicial para temperatura mínima
max_temperature = 27.0  # Valor inicial para temperatura máxima
min_humidity = 30.0     # Valor inicial para umidade mínima
max_humidity = 70.0     # Valor inicial para umidade máxima
logic_enabled = None    # None = lógica desabilitada, "temperature" = lógica de temperatura, "humidity" = lógica de umidade
manual_led_control = True  # Permitir controle manual do LED (True = sim)

# -------------------- Banco de Dados --------------------
client = MongoClient("mongodb://localhost:27017/")
db = client.iot_data
collection = db.sensor_data

# -------------------- Funções Auxiliares --------------------

# Função para log padronizado
def log_message(level, message):
    print(f"[{level}] {message}")

# Função para validar e salvar dados no MongoDB
def save_to_mongodb(temp, hum):
    try:
        temp = float(temp)
        hum = float(hum)
        if -50 <= temp <= 100 and 0 <= hum <= 100:
            data = {
                "temperature": temp,
                "humidity": hum,
                "timestamp": datetime.utcnow()
            }
            collection.insert_one(data)
            log_message("LOG", f"Dados salvos no MongoDB: {data}")
    except ValueError:
        log_message("ERROR", "Dados inválidos, não salvos no MongoDB.")

# Função para aplicar a lógica de cena (umidade ou temperatura)
def apply_scene_logic(temp=None, hum=None):
    global led_state, logic_enabled, manual_led_control

    log_message("LOG", f"Aplicando lógica: {logic_enabled}")

    if logic_enabled == "humidity" and hum is not None:
        if hum > max_humidity and led_state == "Desligado":
            log_message("LOG", f"Umidade ({hum}%) acima de {max_humidity}%, ligando o LED.")
            mqtt_client.publish(mqtt_topic_cmd, "ON")
            set_led_state("Ligado")
        elif hum < min_humidity and led_state == "Ligado":
            log_message("LOG", f"Umidade ({hum}%) abaixo de {min_humidity}%, desligando o LED.")
            mqtt_client.publish(mqtt_topic_cmd, "OFF")
            set_led_state("Desligado")

    elif logic_enabled == "temperature" and temp is not None:
        if temp > max_temperature and led_state == "Ligado":
            log_message("LOG", f"Temperatura ({temp}°C) acima de {max_temperature}°C, desligando o LED.")
            mqtt_client.publish(mqtt_topic_cmd, "OFF")
            set_led_state("Desligado")
        elif temp < min_temperature and led_state == "Desligado":
            log_message("LOG", f"Temperatura ({temp}°C) abaixo de {min_temperature}°C, ligando o LED.")
            mqtt_client.publish(mqtt_topic_cmd, "ON")
            set_led_state("Ligado")

# Função para alterar o estado do LED
def set_led_state(state):
    global led_state
    led_state = state
    log_message("LOG", f"LED {state}")

# -------------------- Funções MQTT --------------------

# Função para conexão ao MQTT
def on_connect(client, userdata, flags, rc):
    log_message("LOG", f"Conectado ao Broker MQTT com resultado {rc}")
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)

# Função para receber mensagens via MQTT
def on_message(client, userdata, msg):
    global temperature, humidity
    try:
        if msg.topic == mqtt_topic_temp:
            temperature = float(msg.payload.decode("utf-8"))
            log_message("LOG", f"Nova temperatura recebida: {temperature}°C")
            apply_scene_logic(temp=temperature)

        elif msg.topic == mqtt_topic_hum:
            humidity = float(msg.payload.decode("utf-8"))
            log_message("LOG", f"Nova umidade recebida: {humidity}%")
            apply_scene_logic(hum=humidity)
            save_to_mongodb(temperature, humidity)

    except ValueError:
        log_message("ERROR", f"Erro ao converter a mensagem: {msg.payload.decode('utf-8')}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Iniciar o cliente MQTT
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

# API para alternar entre lógicas de temperatura ou umidade
@app.post("/api/configuracao")
async def set_sensor_config(request: Request):
    global min_temperature, max_temperature, min_humidity, max_humidity, logic_enabled, manual_led_control
    body = await request.json()

    try:
        logic_type = body.get('logicType')
        manual_led_control = False  # Desabilita o controle manual do LED quando uma lógica estiver ativa

        if logic_type == "temperature":
            min_temperature = float(body['minTemperature'])
            max_temperature = float(body['maxTemperature'])
            logic_enabled = "temperature"
            log_message("LOG", f"Lógica de temperatura habilitada: min={min_temperature}°C, max={max_temperature}°C")
            return {"message": "Configurações de temperatura salvas e lógica habilitada!"}

        elif logic_type == "humidity":
            min_humidity = float(body['minHumidity'])
            max_humidity = float(body['maxHumidity'])
            logic_enabled = "humidity"
            log_message("LOG", f"Lógica de umidade habilitada: min={min_humidity}%, max={max_humidity}%")
            return {"message": "Configurações de umidade salvas e lógica habilitada!"}

        else:
            return JSONResponse(status_code=400, content={"error": "Tipo de lógica inválido."})

    except (ValueError, KeyError):
        log_message("ERROR", "Erro ao salvar configurações.")
        return JSONResponse(status_code=400, content={"error": "Valores de configuração inválidos."})

# API para desabilitar a lógica e habilitar o controle manual do LED
@app.post("/api/toggle-logic")
async def toggle_logic():
    global logic_enabled, manual_led_control
    logic_enabled = None  # Desabilita qualquer lógica ativa
    manual_led_control = True  # Permite controle manual do LED
    mqtt_client.publish(mqtt_topic_cmd, "OFF")  # Desliga o LED ao desabilitar lógica
    set_led_state("Desligado")
    log_message("LOG", "Lógica desativada, controle manual do LED habilitado.")
    return {"message": "Lógica desativada e controle manual do LED habilitado!"}

# API para controlar o LED manualmente (somente se não houver lógica ativa)
@app.get("/api/led/{state}")
async def control_led(state: str):
    global led_state, manual_led_control

    if not manual_led_control:
        return JSONResponse(status_code=403, content={"error": "Controle manual desabilitado, uma lógica está ativa."})

    if state == "on":
        mqtt_client.publish(mqtt_topic_cmd, "ON")
        set_led_state("Ligado")
    elif state == "off":
        mqtt_client.publish(mqtt_topic_cmd, "OFF")
        set_led_state("Desligado")
    return {"status": f"LED {state}"}

# API para buscar o estado atual de temperatura, umidade e LED
@app.get("/api/dados")
async def get_sensor_data():
    return {"temperature": temperature, "humidity": humidity, "led_state": led_state}

# API para buscar dados históricos com base no período
@app.get("/api/dados/{period}")
async def get_sensor_data_period(period: str):
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
