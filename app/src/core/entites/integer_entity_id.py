from .unique_entity_id import EntityID


class IntegerEntityID(EntityID):
    def __init__(self, value=None):
        if value is None:
            raise ValueError("An integer ID must be provided")
        super().__init__(value)
        self.validate()

    def validate(self):
        if not isinstance(self.value, int):
            raise ValueError(f"Invalid Integer ID: {self.value}")

    def __str__(self):
        return str(self.value)
