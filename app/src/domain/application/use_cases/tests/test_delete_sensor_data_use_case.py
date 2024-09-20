import pytest
from typing import List
from app.src.domain.application.use_cases.delete_sensor_data_by_id_use_case import DeleteSensorDataUseCase
from app.src.domain.enterprise.entities.sensor_data import SensorData
from app.tests.repositories.in_memory_sensor_data_repository import InMemorySensorDataRepository
from app.tests.factories.sensor_data_factory import make_sensor_data
from app.src.core.errors.resource_not_found_error import ResourceNotFoundError


@pytest.fixture
def sensor_data_samples() -> List[SensorData]:
    return [
        make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1),
        make_sensor_data(temp=24.0, humi=55.0, led_state="off", id=2)
    ]


@pytest.fixture
def repository(sensor_data_samples: List[SensorData]) -> InMemorySensorDataRepository:
    repository = InMemorySensorDataRepository()
    for data in sensor_data_samples:
        repository.save(data)
    return repository


@pytest.fixture
def delete_use_case(repository: InMemorySensorDataRepository) -> DeleteSensorDataUseCase:
    return DeleteSensorDataUseCase(repository)


def test_delete_sensor_data_success(delete_use_case):
    result = delete_use_case.execute(1)

    assert result.is_right(), "O caso de uso não retornou sucesso ao deletar o dado."
    assert len(delete_use_case.repository.find_all()
               ) == 1, "O número de instâncias não está correto após a exclusão."


def test_delete_sensor_data_not_found(delete_use_case):
    result = delete_use_case.execute(999)

    assert result.is_left(), "O caso de uso deveria falhar ao tentar deletar um ID inexistente."
    assert isinstance(
        result.left_value, ResourceNotFoundError), "O erro retornado não é do tipo esperado."
