from src.core.errors.interfaces.use_case_error import UseCaseError


class InvalidInputError(UseCaseError):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message)
