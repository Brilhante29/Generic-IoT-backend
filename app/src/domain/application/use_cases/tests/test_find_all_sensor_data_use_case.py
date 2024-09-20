import pytest
from typing import List
from app.src.domain.application.use_cases.find_all_sensor_data_use_case import FindAllSensorDataUseCase
from app.tests.repositories.in_memory_sensor_data_repository import InMemorySensorDataRepository
from app.src.domain.enterprise.entities.sensor_data import SensorData
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
def find_all_use_case(repository: InMemorySensorDataRepository) -> FindAllSensorDataUseCase:
    """
    Fixture que inicializa o caso de uso `FindAllSensorDataUseCase` usando o repositório fornecido.
    """
    return FindAllSensorDataUseCase(repository)

def test_find_all_sensor_data_success(find_all_use_case):
    """
    Testa o caso de uso para buscar todos os dados de sensor.
    """
    # Executa o caso de uso
    result = find_all_use_case.execute()

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert len(result.right_value) == 3, "O número de instâncias retornadas não é o esperado."
    assert isinstance(result.right_value[0], SensorData), "Os dados retornados não são do tipo SensorData."
