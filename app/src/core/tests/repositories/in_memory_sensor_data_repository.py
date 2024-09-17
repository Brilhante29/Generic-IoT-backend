from typing import List, Optional
from src.domain.enterprise.entities.sensor_data import SensorData
from src.domain.application.repositories.sensor_data_repository import SensorDataRepository


class InMemorySensorDataRepository(SensorDataRepository):
    items: List[SensorData] = []

    def _clear(self):
        self.items = []

    def save(self, entity: SensorData) -> SensorData:
        self.items = list(map(lambda item: entity if item.id.value == entity.id.value else item, self.items)) \
            if any(item.id.value == entity.id.value for item in self.items) else self.items + [entity]
        return entity

    def find_all(self) -> List[SensorData]:
        return self.items

    def find_by_id(self, id: int) -> Optional[SensorData]:
        return next(filter(lambda item: item.id.value == id, self.items), None)

    def update(self, id: int, entity: SensorData) -> Optional[SensorData]:
        self.items = list(
            map(lambda item: entity if item.id.value == id else item, self.items))
        return entity if any(item.id.value == id for item in self.items) else None

    def delete(self, id: int) -> None:
        self.items = list(filter(lambda item: item.id.value != id, self.items))

    def find_by_led_state(self, led_state: str) -> List[SensorData]:
        return list(filter(lambda item: item.led_state.lower() == led_state.lower(), self.items))

    def find_all_paginated(self, page: int, limit: int) -> List[SensorData]:
        start = (page - 1) * limit
        return self.items[start:start + limit]
