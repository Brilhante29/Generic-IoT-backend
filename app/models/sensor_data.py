from pydantic import BaseModel

class SensorData(BaseModel):
  temp: float
  humi: float
  led_state: str
