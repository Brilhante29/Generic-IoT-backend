import pytest
from typing import List
from app.src.domain.application.use_cases.find_sensor_data_by_led_state_use_case import FindSensorDataByLedStateUseCase
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
def find_by_led_state_use_case(repository: InMemorySensorDataRepository) -> FindSensorDataByLedStateUseCase:
    """
    Fixture que inicializa o caso de uso `FindSensorDataByLedStateUseCase` usando o repositório fornecido.
    """
    return FindSensorDataByLedStateUseCase(repository)


def test_find_sensor_data_by_led_state_on_success(find_by_led_state_use_case):
    """
    Testa o caso de uso para buscar dados de sensor com o LED no estado "on".
    """
    result = find_by_led_state_use_case.execute("on")

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert len(
        result.right_value) == 2, "O número de sensores com LED 'on' não é o esperado."
    assert all(sensor.led_state ==
               "on" for sensor in result.right_value), "Nem todos os sensores têm o LED no estado 'on'."


def test_find_sensor_data_by_led_state_off_success(find_by_led_state_use_case):
    """
    Testa o caso de uso para buscar dados de sensor com o LED no estado "off".
    """
    result = find_by_led_state_use_case.execute("off")

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert len(
        result.right_value) == 1, "O número de sensores com LED 'off' não é o esperado."
    assert all(sensor.led_state ==
               "off" for sensor in result.right_value), "Nem todos os sensores têm o LED no estado 'off'."
