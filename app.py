from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import paho.mqtt.client as mqtt
import threading
from pymongo import MongoClient
from datetime import datetime

app = FastAPI()

# Set up templates
templates = Jinja2Templates(directory="templates")

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

# Function to save valid data to MongoDB and notify WebSocket clients
def save_to_mongodb(temp, hum):
    global temperature, humidity
    if is_valid_data(temp, hum):
        temperature = float(temp)
        humidity = float(hum)
        data = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(data)
        print(f"[LOG] Data saved to MongoDB: {data}")

# Callback when connected to MQTT
def on_connect(client, userdata, flags, rc):
    print(f"[LOG] Connected to MQTT Broker with result code {rc}")
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)

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

# Default route
@app.get("/sistema-antimofo", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/sistema-antimofo/home")

# Home page
@app.get("/sistema-antimofo/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "temperature": temperature, "humidity": humidity, "led_state": led_state})

# API for controlling LED
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

# API to fetch sensor data
@app.get("/api/dados")
async def get_sensor_data():
    print(f"[LOG] Fetching sensor data: Temperature={temperature}, Humidity={humidity}")
    return {"temperature": temperature, "humidity": humidity}

# Start FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
