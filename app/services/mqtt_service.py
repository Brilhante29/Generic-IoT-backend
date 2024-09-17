import paho.mqtt.client as mqtt
import json
from app.models.sensor_data import SensorData

class MQTTService:
    def __init__(self):
        self.mqtt_broker = "test.mosquitto.org"
        self.mqtt_port = 1883
        self.mqtt_topic = "/ThinkIOT/Publish"
        self.sensor_data = SensorData(temp=0.0, humi=0.0, led_state="off")
        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def start(self):
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"[LOG] Connected to MQTT Broker with result code {rc}")
        client.subscribe(self.mqtt_topic)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        try:
            data = json.loads(payload)
            self.sensor_data = SensorData(**data)
            print(f"[LOG] New Data: {self.sensor_data}")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to decode JSON: {e}")

    def publish_data(self):
        self.mqtt_client.publish(self.mqtt_topic, json.dumps(self.sensor_data.dict()))

    def get_sensor_data(self):
        return self.sensor_data
