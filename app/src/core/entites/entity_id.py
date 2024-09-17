from abc import ABC, abstractmethod


class EntityID(ABC):
    def __init__(self, value):
        self.value = value

    @abstractmethod
    def validate(self):
        ...

    def __eq__(self, other):
        if not isinstance(other, EntityID):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)
