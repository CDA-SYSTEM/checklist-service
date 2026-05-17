"""
Manejador global de excepciones para la API REST.

Traduce excepciones de dominio y de infraestructura a respuestas HTTP
estandarizadas con el formato envelope del proyecto.
"""

import logging

from mongoengine.errors import DoesNotExist as MongoDoesNotExist
from mongoengine.errors import ValidationError as MongoValidationError
from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.domain.exceptions import DomainError
from apps.common.presentation.api_response import error_response

logger = logging.getLogger(__name__)

# Mapeo: domain error code → HTTP status code
_DOMAIN_STATUS_MAP = {
    'not_found': 404,
    'conflict': 409,
    'validation_error': 400,
    'service_unavailable': 503,
    'domain_error': 400,
}


def global_exception_handler(exc, context):
    """Handler centralizado que intercepta todas las excepciones no capturadas."""

    # 1. Excepciones de dominio → HTTP status apropiado
    if isinstance(exc, DomainError):
        status = _DOMAIN_STATUS_MAP.get(exc.code, 400)
        return error_response(str(exc), status=status, code=exc.code)

    # 2. MongoEngine DoesNotExist → 404
    if isinstance(exc, MongoDoesNotExist):
        return error_response('Recurso no encontrado.', status=404, code='not_found')

    # 3. MongoEngine ValidationError → 400
    if isinstance(exc, MongoValidationError):
        return error_response(
            'Error de validacion en los datos.',
            status=400,
            code='validation_error',
            details=str(exc),
        )

    # 4. Excepciones DRF estándar (autenticación, permisos, parsing, etc.)
    response = drf_exception_handler(exc, context)
    if response is not None:
        return error_response(
            'Solicitud invalida.',
            status=response.status_code,
            code='request_error',
            details=response.data,
        )

    # 5. Error no controlado → 500 (logear para auditoría)
    logger.exception('Error interno no controlado: %s', exc)
    return error_response(
        'Error interno no controlado.',
        status=500,
        code='internal_error',
    )
