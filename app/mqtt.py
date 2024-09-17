import paho.mqtt.client as mqtt

mqtt_broker = "test.mosquitto.org"
mqtt_port = 1883
mqtt_topic_temp = "/ThinkIOT/temp"
mqtt_topic_hum = "/ThinkIOT/hum"
mqtt_topic_cmd = "/ThinkIOT/Subscribe"

temperature = "N/A"
humidity = "N/A"

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"[LOG] Connected to MQTT Broker with result code {rc}")
    client.subscribe(mqtt_topic_temp)
    client.subscribe(mqtt_topic_hum)

def on_message(client, userdata, msg):
    global temperature, humidity
    if msg.topic == mqtt_topic_temp:
        temperature = msg.payload.decode("utf-8")
    elif msg.topic == mqtt_topic_hum:
        humidity = msg.payload.decode("utf-8")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()

