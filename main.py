from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import paho.mqtt.client as mqtt
import threading
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()

# MQTT configuration
mqtt_broker = "test.mosquitto.org"
mqtt_port = 1883
mqtt_topic_temp = "/ThinkIOT/temp"
mqtt_topic_hum = "/ThinkIOT/hum"
mqtt_topic_cmd = "/ThinkIOT/Subscribe"

# Variables to hold the latest sensor data
temperature = "N/A"
humidity = "N/A"
led_state = "Desligado"

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.iot_data
collection = db.sensor_data

# MQTT Client Setup
mqtt_client = mqtt.Client()

# Function to check if the temperature and humidity are valid
def is_valid_data(temp, hum):
    try:
        temp = float(temp)
        hum = float(hum)
        return -50 <= temp <= 100 and 0 <= hum <= 100
    except ValueError:
        return False

# Function to save valid data to MongoDB
def save_to_mongodb(temp, hum):
    if is_valid_data(temp, hum):
        data = {
            "temperature": float(temp),
            "humidity": float(hum),
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(data)
        print(f"[LOG] Data saved to MongoDB: {data}")
    else:
        print(f"[LOG] Invalid data not saved: Temperature={temp}, Humidity={hum}")

# Callback when connected to MQTT
def on_connect(client, userdata, flags, rc):
    print(f"[LOG] Connected to MQTT Broker with result code {rc}")
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)
    print(f"[LOG] Subscribed to {mqtt_topic_temp} and {mqtt_topic_hum}")

# Callback when receiving messages from MQTT
def on_message(client, userdata, msg):
    global temperature, humidity
    if msg.topic == mqtt_topic_temp:
        temperature = msg.payload.decode("utf-8")
        print(f"[LOG] New Temperature: {temperature}")
    elif msg.topic == mqtt_topic_hum:
        humidity = msg.payload.decode("utf-8")
        print(f"[LOG] New Humidity: {humidity}")
        save_to_mongodb(temperature, humidity)

# Configure the MQTT client
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Start the MQTT loop in a background thread
def start_mqtt():
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Controle de LED e Monitoramento de Temperatura</title>

            <!-- Bootstrap CSS -->
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <!-- Google Material Icons -->
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f0f0f0;  /* Leve tom de cinza */
                }}
                
                /* Sidebar styling */
                .sidebar {{
                    height: 100%;
                    width: 80px;
                    position: fixed;
                    top: 0;
                    left: 0;
                    background-color: #333;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding-top: 20px;
                    transition: width 0.4s;
                    overflow: hidden;
                }}
                .sidebar:hover {{
                    width: 200px;
                }}
                .sidebar i {{
                    font-size: 36px;
                    color: white;
                    margin: 20px 0;
                }}
                .sidebar span {{
                    display: none;
                    font-size: 18px;
                    color: white;
                    white-space: nowrap;
                    padding-left: 10px;
                }}
                .sidebar:hover span {{
                    display: inline-block;
                }}
                .sidebar a {{
                    display: flex;
                    align-items: center;
                    width: 100%;
                    padding-left: 10px;
                }}
                .sidebar a:hover {{
                    background-color: #444;
                }}

                .container {{
                    text-align: center;
                    width: 100%;
                    max-width: 500px;
                    padding: 40px;
                    background-color: #fff;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                
                .data-row {{
                    display: flex;
                    justify-content: space-around;
                    margin-bottom: 20px;
                }}

                .data-display {{
                    font-size: 36px;
                    font-weight: 300;
                    color: #333;
                    margin: 0 20px;
                }}
                
                .data-icon {{
                    font-size: 50px;
                    color: #1E90FF;
                }}

                .toggle-switch {{
                    position: relative;
                    display: inline-block;
                    width: 100px;
                    height: 48px;
                    margin-top: 30px;
                }}
                .toggle-switch input {{
                    opacity: 0;
                    width: 0;
                    height: 0;
                }}
                .slider {{
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: 0.4s;
                    border-radius: 34px;
                    border: 2px solid #ccc;
                }}
                .slider:before {{
                    position: absolute;
                    content: "";
                    height: 40px;
                    width: 40px;
                    left: 4px;
                    bottom: 4px;
                    background-color: white;
                    transition: 0.4s;
                    border-radius: 50%;
                }}
                input:checked + .slider {{
                    background-color: #1E90FF;
                    border-color: #1E90FF;
                }}
                input:checked + .slider:before {{
                    transform: translateX(52px);
                }}

                #ledState {{
                    margin-top: 20px;
                    font-size: 18px;
                    color: #333;
                }}
            </style>
            <script>
                async function ligarLED() {{
                    await fetch('/led/on');
                    document.getElementById("ledState").innerHTML = "LED Ligado";
                }}

                async function desligarLED() {{
                    await fetch('/led/off');
                    document.getElementById("ledState").innerHTML = "LED Desligado";
                }}

                async function toggleLED(checkbox) {{
                    if (checkbox.checked) {{
                        ligarLED();
                    }} else {{
                        desligarLED();
                    }}
                }}

                async function atualizarDados() {{
                    const response = await fetch('/dados');
                    const result = await response.json();
                    document.getElementById("temperatura").innerHTML = result.temperature + "°C";
                    document.getElementById("umidade").innerHTML = result.humidity + "%";
                }}

                setInterval(atualizarDados, 2000);  // Atualizar os dados a cada 2 segundos
            </script>
        </head>
        <body>
            <!-- Sidebar -->
            <div class="sidebar">
                <a href="/"><i class="material-icons">home</i> <span>Home</span></a>
                <a href="/monitoramento"><i class="material-icons">show_chart</i> <span>Monitoramento</span></a>
                <a href="/configuracoes"><i class="material-icons">settings</i> <span>Configurações</span></a>
                <a href="/sobre"><i class="material-icons">info</i> <span>Sobre</span></a>
            </div>

            <!-- Main content -->
            <div class="container">
                <!-- Temperature and Humidity in one row -->
                <div class="data-row">
                    <!-- Temperature -->
                    <div class="data-display">
                        <i class="material-icons data-icon">thermostat</i>
                        <p id="temperatura">N/A°C</p>
                    </div>
                    <!-- Humidity -->
                    <div class="data-display">
                        <i class="material-icons data-icon">opacity</i>
                        <p id="umidade">N/A%</p>
                    </div>
                </div>

                <!-- LED Toggle -->
                <label class="toggle-switch">
                    <input type="checkbox" onclick="toggleLED(this)">
                    <span class="slider round"></span>
                </label>
                <p id="ledState">LED Desligado</p>
            </div>

            <!-- Bootstrap JS (optional) -->
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# API para controle do LED
@app.get("/led/{state}")
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

# API para obter os dados de temperatura e umidade
@app.get("/dados")
async def get_sensor_data():
    print(f"[LOG] Fetching sensor data: Temperature={temperature}, Humidity={humidity}")
    return {"temperature": temperature, "humidity": humidity}

# Monitoramento page
@app.get("/monitoramento", response_class=HTMLResponse)
async def monitoramento():
    content = """
    <h1>Monitoramento de Sensores</h1>
    <p>Exibição de temperatura, umidade e controle de LED.</p>
    """
    return HTMLResponse(content)

# Configurações page
@app.get("/configuracoes", response_class=HTMLResponse)
async def configuracoes():
    content = """
    <h1>Configurações do Sistema</h1>
    <p>Gerencie as configurações do sistema anti-mofo e LED.</p>
    """
    return HTMLResponse(content)

# Sobre page
@app.get("/sobre", response_class=HTMLResponse)
async def sobre():
    content = """
    <h1>Sobre o Sistema</h1>
    <p>Informações sobre o sistema de controle anti-mofo.</p>
    """
    return HTMLResponse(content)

# Iniciar o servidor FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
