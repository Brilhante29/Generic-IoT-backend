from src.core.utils.either import right
from src.domain.application.repositories.sensor_data_repository import SensorDataRepository

class FindAllSensorDataUseCase:
    def __init__(self, repository: SensorDataRepository):
        self.repository = repository

    def execute(self):
        data = self.repository.find_all()
        return right(data)
