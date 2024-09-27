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
        print(f"[LOG] Dados salvos no MongoDB: {data}")

# Função para aplicar a lógica de cena com base na temperatura
def apply_scene_logic(temp):
    global led_state

    # Adiciona logs para depuração
    print(f"[LOG] Aplicando lógica de cena. Temperatura atual: {temp}°C, Lógica desativada: {disable_logic}")

    # Se a lógica está desativada, desliga o LED e retorna
    if disable_logic:
        print("[LOG] Lógica de cena desativada. Desligando o LED.")
        if led_state == "Ligado":
            mqtt_client.publish(mqtt_topic_cmd, "OFF")
            set_led_state("Desligado", temp)
        return  # Retorna se a lógica estiver desativada

    # Converte a temperatura e os limites para float
    try:
        temp = float(temp)
        min_temp = float(min_temperature)
        max_temp = float(max_temperature)
    except ValueError as e:
        print(f"[ERROR] Falha ao converter temperatura: {e}")
        return  # Se ocorrer erro de conversão, não aplica a lógica

    # Forçar o LED a desligar se a temperatura for maior que o máximo
    if temp > max_temp:
        print(f"[LOG] Temperatura ({temp}°C) acima do máximo ({max_temp}°C), forçando o desligamento do LED.")
        mqtt_client.publish(mqtt_topic_cmd, "OFF")
        set_led_state("Desligado", temp)
        return

    # Determinar se o dispositivo precisa ser ligado ou desligado com base nos limites configurados
    if temp < min_temp:
        if led_state == "Desligado":
            print(f"[LOG] Temperatura ({temp}°C) abaixo do mínimo ({min_temp}°C), ligando o LED.")
            mqtt_client.publish(mqtt_topic_cmd, "ON")
            set_led_state("Ligado", temp)
    else:
        print(f"[LOG] Temperatura ({temp}°C) dentro da faixa ideal ({min_temp}°C - {max_temp}°C). Nenhuma ação necessária.")

# Função para alterar o estado do LED
def set_led_state(state, temp):
    global led_state
    led_state = stateset_led_state
    print(f"[LOG] Dispositivo {state}. Temperatura: {temp}°C")

# -------------------- Funções MQTT --------------------

# Callback quando conectar ao MQTT
def on_connect(client, userdata, flags, rc):
    print(f"[LOG] Conectado ao Broker MQTT com resultado {rc}")
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)

# Callback para receber mensagens via MQTT
def on_message(client, userdata, msg):
    global temperature, humidity
    try:
        if msg.topic == mqtt_topic_temp:
            # Converta a mensagem de temperatura recebida para float
            temperature = float(msg.payload.decode("utf-8"))
            print(f"[LOG] Nova temperatura recebida: {temperature}°C")
            apply_scene_logic(temperature)  # Aplica lógica de cena

        elif msg.topic == mqtt_topic_hum:
            humidity = float(msg.payload.decode("utf-8"))
            print(f"[LOG] Nova umidade recebida: {humidity}%")
            save_to_mongodb(temperature, humidity)  # Salva a temperatura e umidade no banco de dados

    except ValueError:
        print(f"[ERROR] Não foi possível converter a mensagem para número: {msg.payload.decode('utf-8')}")
    except Exception as e:
        print(f"[ERROR] Falha ao processar a mensagem: {e}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Função para iniciar o loop do MQTT em uma thread separada
def start_mqtt():
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# -------------------- Rotas de API --------------------

# Rota padrão para redirecionar à página principal
@app.get("/sistema-antimofo", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/sistema-antimofo/home")

# Página Home
@app.get("/sistema-antimofo/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "temperature": temperature, "humidity": humidity, "led_state": led_state})

# Página de Monitoramento
@app.get("/sistema-antimofo/monitoramento", response_class=HTMLResponse)
async def monitoramento(request: Request):
    return templates.TemplateResponse("monitoramento.html", {"request": request})

# Página de Configurações
@app.get("/sistema-antimofo/configuracoes", response_class=HTMLResponse)
async def configuracoes(request: Request):
    return templates.TemplateResponse("configuracoes.html", {"request": request})

# Página Sobre
@app.get("/sistema-antimofo/sobre", response_class=HTMLResponse)
async def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request})

# API para alternar a lógica de cena (habilitar/desabilitar)
@app.post("/api/toggle-logic")
async def toggle_logic():
    global disable_logic
    disable_logic = not disable_logic  # Alterna o estado de habilitação/desabilitação
    message = "Lógica de cena desabilitada!" if disable_logic else "Lógica de cena habilitada!"

    # Se a lógica foi desativada, desligue o LED
    if disable_logic and led_state == "Ligado":
        mqtt_client.publish(mqtt_topic_cmd, "OFF")
        set_led_state("Desligado", temperature)
        print("[LOG] Lógica desativada e LED desligado.")

    return {"message": message, "disable_logic": disable_logic}

# API para salvar as configurações de temperatura mínima e máxima
@app.post("/api/configuracao")
async def set_temperature_config(request: Request):
    global min_temperature, max_temperature
    body = await request.json()
    try:
        min_temperature = float(body['minTemperature'])
        max_temperature = float(body['maxTemperature'])
        print(f"[LOG] Configurações salvas: min_temperature={min_temperature}, max_temperature={max_temperature}")
        return {"message": "Configurações salvas com sucesso!"}
    except (ValueError, KeyError):
        print("[ERROR] Valores de configuração inválidos.")
        return JSONResponse(status_code=400, content={"error": "Valores de configuração inválidos."})

# API para buscar o estado atual da lógica
@app.get("/api/get-logic-state")
async def get_logic_state():
    return {"disable_logic": disable_logic}

# API para salvar as configurações de temperatura mínima e máxima, e desativar lógica
@app.post("/api/configuracao")
async def set_temperature_config(request: Request):
    global min_temperature, max_temperature
    body = await request.json()
    try:
        min_temperature = float(body['minTemperature'])
        max_temperature = float(body['maxTemperature'])
        return {"message": "Configurações salvas!"}
    except (ValueError, KeyError):
        return JSONResponse(status_code=400, content={"error": "Valores de configuração inválidos."})

# API para controlar o LED
@app.get("/api/led/{state}")
async def control_led(state: str):
    global led_state
    if state == "on":
        mqtt_client.publish(mqtt_topic_cmd, "ON")
        led_state = "Ligado"
        print(f"[LOG] Published ON command to topic {mqtt_topic_cmd}")
    elif state == "off":
        mqtt_client.publish(mqtt_topic_cmd, "OFF")
        led_state = "Desligado"
        print(f"[LOG] Published OFF command to topic {mqtt_topic_cmd}")
    return {"status": f"LED {state}"}

# API para buscar os dados do sensor
@app.get("/api/dados")
async def get_sensor_data():
    print(f"[LOG] Fetching sensor data: Temperature={temperature}, Humidity={humidity}")
    return {"temperature": temperature, "humidity": humidity}

# API para buscar dados de temperatura, umidade e LED com base no período
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

# API para alternar a lógica de cena (habilitar/desabilitar)
@app.post("/api/toggle-logic")
async def toggle_logic():
    global disable_logic
    disable_logic = not disable_logic  # Alterna o estado de habilitação/desabilitação
    message = "Lógica de cena desabilitada!" if disable_logic else "Lógica de cena habilitada!"
    print(f"[LOG] {message}")
    return {"message": message, "disable_logic": disable_logic}

# -------------------- Inicialização do Servidor --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
