from app.src.core.entites.entity_id import EntityID


class IntegerEntityID(EntityID):
    _id_counter = 0

    def __init__(self, value=None):
        """
        Inicializa um IntegerEntityID. Se nenhum valor for fornecido, 
        um ID incremental será gerado automaticamente.
        """
        # Se o valor for None, gera um novo ID incremental.
        value = value if isinstance(value, int) else self._generate_id()
        super().__init__(value)
        self.validate()

    def _generate_id(self):
        """
        Gera um ID incremental.
        
        Returns:
            int: Um novo ID incremental.
        """
        IntegerEntityID._id_counter += 1
        return IntegerEntityID._id_counter

    def validate(self):
        """
        Valida o ID, garantindo que seja um inteiro.
        """
        if not isinstance(self.value, int):
            raise ValueError(f"Invalid Integer ID: {self.value}")

    def __str__(self):
        return str(self.value)
