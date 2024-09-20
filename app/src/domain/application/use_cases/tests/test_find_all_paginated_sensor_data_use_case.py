import pytest
from typing import List
from app.src.domain.application.use_cases.find_all_paginated_sensor_data_use_case import FindAllPaginatedSensorDataUseCase
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
        make_sensor_data(temp=25.5, humi=50.0, led_state="on", id=3),
        make_sensor_data(temp=23.0, humi=58.0, led_state="off", id=4),
        make_sensor_data(temp=26.0, humi=53.0, led_state="on", id=5)
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
def find_all_paginated_use_case(repository: InMemorySensorDataRepository) -> FindAllPaginatedSensorDataUseCase:
    """
    Fixture que inicializa o caso de uso `FindAllPaginatedSensorDataUseCase` usando o repositório fornecido.
    """
    return FindAllPaginatedSensorDataUseCase(repository)

def test_find_all_paginated_sensor_data_page_1(find_all_paginated_use_case):
    """
    Testa o caso de uso para buscar dados de sensor paginados (primeira página).
    """
    result = find_all_paginated_use_case.execute(page=1, limit=2)

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert len(result.right_value) == 2, "O número de sensores na página 1 não é o esperado."

def test_find_all_paginated_sensor_data_page_2(find_all_paginated_use_case):
    """
    Testa o caso de uso para buscar dados de sensor paginados (segunda página).
    """
    result = find_all_paginated_use_case.execute(page=2, limit=2)

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert len(result.right_value) == 2, "O número de sensores na página 2 não é o esperado."

def test_find_all_paginated_sensor_data_page_3(find_all_paginated_use_case):
    """
    Testa o caso de uso para buscar dados de sensor paginados (terceira página).
    """
    result = find_all_paginated_use_case.execute(page=3, limit=2)

    # Verificações
    assert result.is_right(), "O caso de uso não retornou sucesso."
    assert len(result.right_value) == 1, "O número de sensores na página 3 não é o esperado."
