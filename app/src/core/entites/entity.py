from app.src.core.entites.entity_id import EntityID
from abc import ABC


class Entity(ABC):
    def __init__(self, id: EntityID = None):
        self._id = id or UniqueEntityID()

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        return isinstance(other, Entity) and self is other or self._id == getattr(other, 'id', None)
