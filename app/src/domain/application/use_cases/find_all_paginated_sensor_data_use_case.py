from app.src.core.errors.invalid_input_error import InvalidInputError
from app.src.core.utils.either import left, right
from app.src.domain.application.repositories.sensor_data_repository import SensorDataRepository


class FindAllPaginatedSensorDataUseCase:
    def __init__(self, repository: SensorDataRepository):
        self.repository = repository

    def execute(self, page: int, limit: int):
        if page < 1 or limit < 1:
            return left(InvalidInputError("Page and limit must be positive integers"))
        data = self.repository.find_all_paginated(page, limit)
        return right(data)
