from app.src.core.errors.invalid_input_error import InvalidInputError
from app.src.core.errors.resource_not_found_error import ResourceNotFoundError
from app.src.core.utils.either import left, right
from app.src.domain.application.repositories.sensor_data_repository import SensorDataRepository


class FindSensorDataByIdUseCase:
    def __init__(self, repository: SensorDataRepository):
        self.repository = repository

    def execute(self, id: int):
        if not id:
            return left(InvalidInputError("ID must be provided"))
        sensor_data = self.repository.find_by_id(id)
        if sensor_data is None:
            return left(ResourceNotFoundError(f"No sensor data found for ID: {id}"))
        return right(sensor_data)
