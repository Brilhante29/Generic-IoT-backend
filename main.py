from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import paho.mqtt.client as mqtt
import threading

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

# MQTT Client Setup
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"[LOG] Connected to MQTT Broker with result code {rc}")
    # Subscribe to the temperature and humidity topics
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)
    print(f"[LOG] Subscribed to {mqtt_topic_temp} and {mqtt_topic_hum}")

def on_message(client, userdata, msg):
    global temperature, humidity
    print(f"[LOG] Message received from topic: {msg.topic}")
    if msg.topic == mqtt_topic_temp:
        temperature = msg.payload.decode("utf-8")
        print(f"[LOG] New Temperature: {temperature}")
    elif msg.topic == mqtt_topic_hum:
        humidity = msg.payload.decode("utf-8")
        print(f"[LOG] New Humidity: {humidity}")

# Configure the MQTT client
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Start the MQTT loop in a background thread
def start_mqtt():
    print("[LOG] Starting MQTT Client")
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

@app.get("/", response_class=HTMLResponse)
async def control_page():
    print("[LOG] Control page accessed")
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Controle de LED e Monitoramento de Temperatura</title>
            <script>
                async function ligarLED() {{
                    await fetch('/led/on');
                }}

                async function desligarLED() {{
                    await fetch('/led/off');
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
            <h1>Controle de LED e Monitoramento de Temperatura</h1>
            <p id="temperatura">Temperatura: N/A</p>
            <p id="umidade">Umidade: N/A</p>
            <button onclick="ligarLED()">Ligar LED</button>
            <button onclick="desligarLED()">Desligar LED</button>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/led/{state}")
async def control_led(state: str):
    print(f"[LOG] LED control: {state}")
    if state == "on":
        mqtt_client.publish(mqtt_topic_cmd, "ON")  # Publica comando para ligar o LED
        print(f"[LOG] Published ON command to topic {mqtt_topic_cmd}")
    elif state == "off":
        mqtt_client.publish(mqtt_topic_cmd, "OFF")  # Publica comando para desligar o LED
        print(f"[LOG] Published OFF command to topic {mqtt_topic_cmd}")
    return {"status": f"LED {state}"}

@app.get("/dados")
async def get_sensor_data():
    print(f"[LOG] Fetching sensor data: Temperature={temperature}, Humidity={humidity}")
    return {"temperature": temperature, "humidity": humidity}
