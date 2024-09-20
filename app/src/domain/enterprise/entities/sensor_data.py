from datetime import datetime
from app.src.core.entites.integer_entity_id import IntegerEntityID
from app.src.core.entites.entity import Entity


class SensorData(Entity):
    def __init__(self, temp: float, humi: float, led_state: str, id=None, timestamp: datetime = None):
        """
        Inicializa uma instância de SensorData.

        Args:
            temp (float): Temperatura do sensor.
            humi (float): Umidade do sensor.
            led_state (str): Estado do LED ("on" ou "off").
            id (int): ID do sensor. Se não fornecido, um ID incremental será gerado.
            timestamp (datetime): Timestamp opcional. Se não fornecido, será utilizado o valor atual.
        """
        # Agora, não é necessário verificar o ID. IntegerEntityID cuidará disso.
        super().__init__(IntegerEntityID(id))
        self.temp = temp
        self.humi = humi
        self.led_state = led_state
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        """
        Retorna um dicionário representando os dados do sensor.
        """
        return {
            "id": str(self.id),
            "temp": self.temp,
            "humi": self.humi,
            "led_state": self.led_state,
            "timestamp": self.timestamp.isoformat(),
        }

    def __eq__(self, other):
        """
        Compara dois objetos SensorData com base no ID.
        """
        return isinstance(other, SensorData) and self.id == other.id