import pytest
from src.core.errors.resource_not_found_error import ResourceNotFoundError
from app.src.core.tests.repositories.in_memory_sensor_data_repository import (
    InMemoryTravelOptionRepository,
)

from src.domain.application.use_cases.find_travel_option_by_city import (
    FindTravelOptionsByCityUseCase,
)
from app.src.domain.enterprise.entities.sensor_data import TravelOption


@pytest.fixture
def travel_options():
    return [
        TravelOption(
            name="Expresso Oriente",
            price_confort=205.10,
            price_econ=121.50,
            city="São Paulo",
            duration="12h",
            seat="1A",
            bed="4D",
        ),
        TravelOption(
            name="Linha Azul",
            price_confort=150.00,
            price_econ=90.00,
            city="São Paulo",
            duration="10h",
            seat="2B",
            bed="3C",
        ),
        TravelOption(
            name="Rápido Fenix",
            price_confort=180.00,
            price_econ=110.00,
            city="Rio de Janeiro",
            duration="8h",
            seat="4D",
            bed="5A",
        ),
    ]


@pytest.fixture
def repository(travel_options):
    repository = InMemoryTravelOptionRepository()
    repository._clear()
    for option in travel_options:
        repository.save(option)
    return repository


@pytest.fixture
def use_case(repository):
    return FindTravelOptionsByCityUseCase(repository)


def test_get_travel_options_by_city_with_valid_city_returns_right(use_case):
    city = "São Paulo"
    result = use_case.execute(city)
    assert result.is_right()
    options = result.right_value
    assert all(option.city == city for option in options)

def test_get_travel_options_by_city_with_invalid_city_returns_left(use_case):
    city = "Cidade Inexistente"
    result = use_case.execute(city)
    assert result.is_left()
    assert isinstance(result.left_value, ResourceNotFoundError)