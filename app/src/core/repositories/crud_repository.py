from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from src.core.repositories.pagination import (
    PaginatedResult,
    PaginationParams,
)

T = TypeVar("T")
ID = TypeVar("ID")


class CrudRepository(ABC, Generic[T, ID]):
    @abstractmethod
    def save(self, entity: T) -> T:
        ...

    @abstractmethod
    def find_all(self) -> List[T]:
        ...

    @abstractmethod
    def find_all_paginated(self, pagination: PaginationParams) -> PaginatedResult[T]:
        ...

    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        ...

    @abstractmethod
    def update(self, id: ID, entity: T) -> T:
        ...

    @abstractmethod
    def delete(self, id: ID) -> None:
        ...
