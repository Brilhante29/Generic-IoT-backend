from src.core.errors.invalid_input_error import InvalidInputError
from src.core.utils.either import left, right
from src.domain.application.repositories.sensor_data_repository import SensorDataRepository
from src.domain.enterprise.entities.sensor_data import SensorData

class SaveSensorDataUseCase:
    def __init__(self, repository: SensorDataRepository):
        self.repository = repository

    def execute(self, sensor_data: SensorData):
        if not sensor_data:
            return left(InvalidInputError("SensorData must be provided"))
        saved_data = self.repository.save(sensor_data)
        return right(saved_data)
