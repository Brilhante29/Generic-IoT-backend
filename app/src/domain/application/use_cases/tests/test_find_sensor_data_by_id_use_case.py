import pytest
from typing import List
from app.src.domain.application.use_cases.find_sensor_data_by_id_use_case import FindSensorDataByIdUseCase
from app.tests.repositories.in_memory_sensor_data_repository import InMemorySensorDataRepository
from app.src.domain.enterprise.entities.sensor_data import SensorData
from app.src.core.errors.resource_not_found_error import ResourceNotFoundError
from app.tests.factories.sensor_data_factory import make_sensor_data

@pytest.fixture
def sensor_data_samples() -> List[SensorData]:
    """
    Fixture que retorna uma lista de dados de sensores para os testes.
    """
    return [
        make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1),
        make_sensor_data(temp=24.0, humi=55.0, led_state="off", id=2),
        make_sensor_data(temp=25.5, humi=50.0, led_state="on", id=3)
    ]

@pytest.fixture
def repository(sensor_data_samples: List[SensorData]) -> InMemorySensorDataRepository:
    """
    Fixture que inicializa um repositório em memória e salva os dados de sensores nele.
    """
    repository = InMemorySensorDataRepository()
    for data in sensor_data_samples:
        repository.save(data)
    return repository

@pytest.fixture
def find_by_id_use_case(repository: InMemorySensorDataRepository) -> FindSensorDataByIdUseCase:
    """
    Fixture que inicializa o caso de uso `FindSensorDataByIdUseCase` usando o repositório fornecido.
    """
    return FindSensorDataByIdUseCase(repository)

def test_find_sensor_data_by_id_success(find_by_id_use_case):
    """
    Testa o caso de uso para buscar um dado de sensor pelo ID.
    """
    # Executa o caso de uso com ID válido
    result = find_by_id_use_case.execute(1)

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert result.right_value.id.value == 1, "O ID do dado retornado não é o esperado."

def test_find_sensor_data_by_id_not_found(find_by_id_use_case):
    """
    Testa o caso de uso para buscar um dado de sensor por um ID inexistente.
    """
    # Executa o caso de uso com ID inválido
    result = find_by_id_use_case.execute(999)

    # Verificações
    assert result.is_left(), "O caso de uso deveria falhar com ID inexistente."
    assert isinstance(result.left_value, ResourceNotFoundError), "O erro retornado não é do tipo esperado."
