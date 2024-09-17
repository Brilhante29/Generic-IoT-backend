from src.core.errors.invalid_input_error import InvalidInputError
from src.core.utils.either import left, right
from src.domain.application.repositories.sensor_data_repository import SensorDataRepository

class FindSensorDataByLedStateUseCase:
    def __init__(self, repository: SensorDataRepository):
        self.repository = repository

    def execute(self, led_state: str):
        if not led_state:
            return left(InvalidInputError("LED state must be provided"))
        data = self.repository.find_by_led_state(led_state)
        return right(data)
