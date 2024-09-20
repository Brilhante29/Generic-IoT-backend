from typing import Optional
from datetime import datetime
from faker import Faker
from app.src.domain.enterprise.entities.sensor_data import SensorData


def make_sensor_data(
    temp: Optional[float] = None,
    humi: Optional[float] = None,
    led_state: Optional[str] = None,
    id: Optional[int] = None,
    timestamp: Optional[datetime] = None
) -> SensorData:
    """
    Factory function to create SensorData instances with random data using Faker.

    Args:
        temp (Optional[float]): Temperature value for the sensor. If None, a random value between 15°C and 35°C will be generated.
        humi (Optional[float]): Humidity value for the sensor. If None, a random value between 40% and 80% will be generated.
        led_state (Optional[str]): The state of the LED ("on" or "off"). If None, a random state will be generated.
        id (Optional[int]): Optional integer ID for the sensor. If None, an incremental ID will be generated automatically.
        timestamp (Optional[datetime]): Optional timestamp for the data. If None, the current time will be used.

    Returns:
        SensorData: A new instance of SensorData with either provided or random data.
    """
    # Inicializando o Faker
    faker = Faker()

    # Gerando dados aleatórios com Faker se não forem fornecidos
    # Temperatura entre 15°C e 35°C
    temp = temp or round(faker.random.uniform(15, 35), 1)
    humi = humi or round(faker.random.uniform(
        40, 80), 1)  # Umidade entre 40% e 80%
    led_state = led_state or faker.random_element(elements=("on", "off"))

    # Criando e retornando a instância de SensorData
    return SensorData(temp=temp, humi=humi, led_state=led_state, id=id, timestamp=timestamp or datetime.now())
