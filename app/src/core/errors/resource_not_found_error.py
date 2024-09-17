from src.core.errors.interfaces.use_case_error import UseCaseError


class ResourceNotFoundError(UseCaseError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
