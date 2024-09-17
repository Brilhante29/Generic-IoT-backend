import uuid

from src.core.entites.entity_id import EntityID


class UniqueEntityID(EntityID):
    def __init__(self, value=None):
        if value is None:
            value = uuid.uuid4()
        super().__init__(value)
        self.validate()

        def validate(self):
            if not isinstance(self.value, uuid.UUID):
                raise ValueError(f"Invalid UUID: {self.value}")

        def __str__(self):
            return str(self.value)
