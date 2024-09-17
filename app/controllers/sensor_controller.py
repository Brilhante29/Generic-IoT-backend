from app.services.mqtt_service import MQTTService

class SensorController:
  def __init__(self):
    self.mqtt_service = MQTTService()

  def get_sensor_data(self):
    return self.mqtt_service.get_sensor_data().model_dump()
