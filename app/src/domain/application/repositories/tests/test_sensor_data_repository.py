import pytest
from app.tests.factories.sensor_data_factory import make_sensor_data
from app.tests.repositories.in_memory_sensor_data_repository import InMemorySensorDataRepository

@pytest.fixture
def repository():
    return InMemorySensorDataRepository()

def test_save_sensor_data(repository):
    sensor_data = make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1)
    saved_data = repository.save(sensor_data)
    assert saved_data == sensor_data
    assert len(repository.find_all()) == 1

def test_find_sensor_data_by_id(repository):
    sensor_data = make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1)
    repository.save(sensor_data)
    
    found_data = repository.find_by_id(1)
    assert found_data is not None
    assert found_data.id.value == 1

def test_delete_sensor_data(repository):
    sensor_data = make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1)
    repository.save(sensor_data)
    
    repository.delete(1)
    assert repository.find_by_id(1) is None
    assert len(repository.find_all()) == 0

def test_update_sensor_data(repository):
    sensor_data = make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1)
    repository.save(sensor_data)

    updated_sensor_data = make_sensor_data(temp=30.0, humi=70.0, led_state="off", id=1)
    repository.update(1, updated_sensor_data)

    found_data = repository.find_by_id(1)
    assert found_data.temp == 30.0
    assert found_data.humi == 70.0
    assert found_data.led_state == "off"

def test_find_by_led_state(repository):
    sensor_data_on = make_sensor_data(temp=22.5, humi=60.0, led_state="on", id=1)
    sensor_data_off = make_sensor_data(temp=24.0, humi=55.0, led_state="off", id=2)
    
    repository.save(sensor_data_on)
    repository.save(sensor_data_off)

    found_data = repository.find_by_led_state("on")
    assert len(found_data) == 1
    assert found_data[0].led_state == "on"
    
    found_data = repository.find_by_led_state("off")
    assert len(found_data) == 1
    assert found_data[0].led_state == "off"

def test_find_all_paginated(repository):
    # Criando 5 entradas de dados de sensor
    for i in range(1, 6):
        repository.save(make_sensor_data(id=i))

    # Testando a paginação (limit = 2, page = 1)
    page_1_data = repository.find_all_paginated(page=1, limit=2)
    assert len(page_1_data) == 2

    # Testando a paginação (limit = 2, page = 2)
    page_2_data = repository.find_all_paginated(page=2, limit=2)
    assert len(page_2_data) == 2

    # Testando a ultima página com um item restante
    page_3_data = repository.find_all_paginated(page=3, limit=2)
    assert len(page_3_data) == 1
