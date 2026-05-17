"""
Excepciones de dominio del checklist-service.

Estas excepciones son puras del dominio: NO contienen conceptos HTTP.
El mapeo a códigos HTTP se realiza en la capa de presentación
(exception_handlers.py).
"""


class DomainError(Exception):
    """Excepción base para errores de dominio."""

    code = 'domain_error'

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        if code:
            self.code = code


class NotFoundError(DomainError):
    """Recurso no encontrado en el dominio."""

    code = 'not_found'


class ConflictError(DomainError):
    """Conflicto de estado o duplicado en el dominio."""

    code = 'conflict'


class ValidationError(DomainError):
    """Error de validación de reglas de negocio."""

    code = 'validation_error'


class ServiceUnavailableError(DomainError):
    """Servicio externo no disponible (RabbitMQ, etc.)."""

    code = 'service_unavailable'
