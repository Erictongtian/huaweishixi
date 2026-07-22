class BusinessException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


class PermissionException(Exception):
    def __init__(self, message: str = "Permission denied"):
        self.message = message


class NotFoundException(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message


class ConflictException(Exception):
    def __init__(self, message: str = "Resource conflict"):
        self.message = message


class ValidationException(Exception):
    def __init__(self, message: str = "Validation error", errors: list | None = None):
        self.message = message
        self.errors = errors or []