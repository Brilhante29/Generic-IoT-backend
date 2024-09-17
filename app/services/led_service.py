from app.services.mqtt_service import MQTTService

class LEDService:
  def __init__(self, mqtt_service: MQTTService):
    self.mqtt_service = mqtt_service

  def set_led_state(self, state: str):
    if state in ["on", "off"]:
      self.mqtt_service.sensor_data.led_state = state
      self.mqtt_service.publish_data()
      return {"status": f"LED {state}"}
    else:
      return {"error": "Invalid LED state"}, 400
