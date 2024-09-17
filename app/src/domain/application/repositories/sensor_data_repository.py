from abc import ABC, abstractmethod
from typing import List, Optional
from app.src.domain.enterprise.entities.sensor_data import SensorData

class SensorDataRepository(ABC):
    """
    Interface abstrata para o repositório de dados de sensores.
    
    Essa interface define métodos para manipular registros da entidade SensorData,
    como operações de salvar, buscar, atualizar e deletar, além de consultas específicas,
    como busca por estado do LED e paginação de resultados.
    """

    @abstractmethod
    def save(self, entity: SensorData) -> SensorData:
        """
        Salva ou atualiza um registro de SensorData no repositório.
        
        Args:
            entity (SensorData): O objeto SensorData a ser salvo ou atualizado.
        
        Returns:
            SensorData: O objeto SensorData salvo ou atualizado.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[SensorData]:
        """
        Retorna todos os registros de SensorData no repositório.
        
        Returns:
            List[SensorData]: Uma lista contendo todos os registros de SensorData.
        """
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[SensorData]:
        """
        Busca um registro de SensorData pelo ID.

        Args:
            id (int): O ID do registro a ser buscado.

        Returns:
            Optional[SensorData]: O objeto SensorData encontrado ou None se não for encontrado.
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """
        Remove um registro de SensorData do repositório com base no ID.

        Args:
            id (int): O ID do registro a ser removido.
        
        Returns:
            None
        """
        pass

    @abstractmethod
    def find_by_led_state(self, led_state: str) -> List[SensorData]:
        """
        Busca todos os registros de SensorData que possuem o estado do LED especificado.
        
        Args:
            led_state (str): O estado do LED (ex.: "on", "off") para buscar os registros.

        Returns:
            List[SensorData]: Uma lista de registros de SensorData com o estado do LED especificado.
        """
        pass

    @abstractmethod
    def find_all_paginated(self, page: int, limit: int) -> List[SensorData]:
        """
        Retorna uma lista paginada de registros de SensorData com base nos parâmetros de paginação.

        Args:
            page (int): O número da página (1 para a primeira página).
            limit (int): O número máximo de registros por página.

        Returns:
            List[SensorData]: Uma lista paginada de registros de SensorData.
        """
        pass
