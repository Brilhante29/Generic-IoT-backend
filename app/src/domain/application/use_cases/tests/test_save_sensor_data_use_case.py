import pytest
from app.tests.factories.sensor_data_factory import make_sensor_data
from app.src.core.errors.invalid_input_error import InvalidInputError
from app.src.domain.enterprise.entities.sensor_data import SensorData
from app.src.domain.application.use_cases.save_sensor_data_use_case import SaveSensorDataUseCase
from app.tests.repositories.in_memory_sensor_data_repository import InMemorySensorDataRepository

@pytest.fixture
def repository() -> InMemorySensorDataRepository:
    """
    Fixture que inicializa um repositório em memória.
    """
    return InMemorySensorDataRepository()

@pytest.fixture
def save_use_case(repository: InMemorySensorDataRepository) -> SaveSensorDataUseCase:
    """
    Fixture que inicializa o caso de uso `SaveSensorDataUseCase` usando o repositório fornecido.
    """
    return SaveSensorDataUseCase(repository)

def test_save_sensor_data_success(save_use_case):
    """
    Testa o caso de uso de salvar dados de sensor com uma entrada válida.
    """
    # Gerando dados do sensor usando a factory
    sensor_data = make_sensor_data(temp=22.5, humi=60.0, led_state="on")
    
    # Executa o caso de uso com dados válidos
    result = save_use_case.execute(sensor_data)

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert isinstance(result.right_value, SensorData), "O valor retornado não é uma instância de SensorData."

def test_save_sensor_data_with_invalid_input(save_use_case):
    """
    Testa o caso de uso de salvar dados de sensor com entrada inválida (None).
    """
    # Executa o caso de uso com entrada inválida (None)
    result = save_use_case.execute(None)

    # Verificações
    assert result.is_left(), "O caso de uso deveria falhar com entrada inválida."
    assert isinstance(result.left_value, InvalidInputError), "O erro retornado não é do tipo esperado."
