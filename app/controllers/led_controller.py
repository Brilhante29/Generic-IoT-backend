from app.services.led_service import LEDService
from app.services.mqtt_service import MQTTService

class LEDController:
  def __init__(self):
    self.mqtt_service = MQTTService()
    self.led_service = LEDService(self.mqtt_service)

  def control_led(self, state: str):
    return self.led_service.set_led_state(state)
