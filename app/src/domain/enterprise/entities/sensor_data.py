from datetime import datetime
from src.core.entites.integer_entity_id import IntegerEntityID
from src.core.entites.entity import Entity


class SensorData(Entity):
    def __init__(self, temp: float, humi: float, led_state: str, id=None, timestamp: datetime = None):
        id = IntegerEntityID(id) if isinstance(id, int) else None
        super().__init__(id)
        self.temp = temp
        self.humi = humi
        self.led_state = led_state
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            "id": str(self.id),
            "temp": self.temp,
            "humi": self.humi,
            "led_state": self.led_state,
            "timestamp": self.timestamp.isoformat(),
        }

    def __eq__(self, other):
        return isinstance(other, SensorData) and self.id == other.id
