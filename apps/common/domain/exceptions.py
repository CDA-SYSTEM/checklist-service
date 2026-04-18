class DomainError(Exception):
    status_code = 400
    code = 'domain_error'

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        if code:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(DomainError):
    status_code = 404
    code = 'not_found'


class ConflictError(DomainError):
    status_code = 409
    code = 'conflict'


class ValidationError(DomainError):
    status_code = 400
    code = 'validation_error'
