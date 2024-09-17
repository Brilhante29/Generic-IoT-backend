import pytest
from src.core.errors.invalid_input_error import InvalidInputError
from src.core.errors.resource_not_found_error import ResourceNotFoundError
from app.src.domain.enterprise.entities.sensor_data import TravelOption
from src.domain.application.use_cases.find_most_comfortable_and_fastest_travel_option_for_city import (
    FindMostComfortableAndFastestTravelOptionForCityUseCase,
)
from app.src.core.tests.repositories.in_memory_sensor_data_repository import (
    InMemoryTravelOptionRepository,
)


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
    for option in travel_options:
        repository.save(option)
    return repository


@pytest.fixture
def use_case(repository):
    return FindMostComfortableAndFastestTravelOptionForCityUseCase(repository)


def test_find_most_comfortable_and_fastest_with_valid_city_returns_right(use_case):
    city = "São Paulo"
    result = use_case.execute(city)
    assert result.is_right()
    assert result.right_value.name == "Expresso Oriente"


def test_find_most_comfortable_and_fastest_with_invalid_city_returns_left(use_case):
    city = "Cidade Inexistente"
    result = use_case.execute(city)
    assert result.is_left()
    assert isinstance(result.left_value, ResourceNotFoundError)


def test_find_most_comfortable_and_fastest_with_empty_city_returns_left(use_case):
    # Dado
    city = ""
    # Quando
    result = use_case.execute(city)
    # Então
    assert result.is_left()
    assert isinstance(result.left_value, InvalidInputError)
