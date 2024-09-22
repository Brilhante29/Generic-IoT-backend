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

# Main control page
@app.get("/", response_class=HTMLResponse)
async def control_page():
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Controle de LED e Monitoramento de Temperatura</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; display: flex; }}
                
                .sidebar {{
                    height: 100%;
                    width: 200px;
                    position: fixed;
                    top: 0;
                    left: 0;
                    background-color: #333;
                    padding-top: 20px;
                    color: white;
                }}

                .sidebar a {{
                    padding: 10px 15px;
                    text-decoration: none;
                    font-size: 18px;
                    color: white;
                    display: block;
                }}

                .sidebar a:hover {{
                    background-color: #575757;
                }}

                .content {{
                    margin-left: 220px;  /* Espaço para a sidebar */
                    padding: 20px;
                }}

                .toggle-switch {{
                    position: relative;
                    display: inline-block;
                    width: 60px;
                    height: 34px;
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
                }}

                .slider:before {{
                    position: absolute;
                    content: "";
                    height: 26px;
                    width: 26px;
                    left: 4px;
                    bottom: 4px;
                    background-color: white;
                    transition: 0.4s;
                }}

                input:checked + .slider {{
                    background-color: green;
                }}

                input:checked + .slider:before {{
                    transform: translateX(26px);
                }}

                .slider.round {{
                    border-radius: 34px;
                }}

                .slider.round:before {{
                    border-radius: 50%;
                }}

                #ledState {{
                    margin-top: 20px;
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
                    document.getElementById("temperatura").innerHTML = "Temperatura: " + result.temperature + " °C";
                    document.getElementById("umidade").innerHTML = "Umidade: " + result.humidity + " %";
                }}

                setInterval(atualizarDados, 2000);  // Atualizar os dados a cada 2 segundos
            </script>
        </head>
        <body>
            <div class="sidebar">
                <h2>Navegação</h2>
                <a href="#">Home</a>
                <a href="#">Monitoramento</a>
                <a href="#">Configurações</a>
                <a href="#">Sobre</a>
            </div>
            
            <div class="content">
                <h1>Controle de LED e Monitoramento de Temperatura</h1>
                <p id="temperatura">Temperatura: N/A</p>
                <p id="umidade">Umidade: N/A</p>

                <label class="toggle-switch">
                    <input type="checkbox" onclick="toggleLED(this)">
                    <span class="slider round"></span>
                </label>
                <p id="ledState">LED Desligado</p>
            </div>
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

# Iniciar o servidor FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
