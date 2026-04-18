from mongoengine.errors import DoesNotExist as MongoDoesNotExist
from mongoengine.errors import ValidationError as MongoValidationError
from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.domain.exceptions import DomainError
from apps.common.presentation.api_response import error_response


def global_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return error_response(str(exc), status=exc.status_code, code=exc.code)

    if isinstance(exc, MongoDoesNotExist):
        return error_response('Recurso no encontrado.', status=404, code='not_found')

    if isinstance(exc, MongoValidationError):
        return error_response('Error de validacion en MongoDB.', status=400, code='validation_error', details=str(exc))

    response = drf_exception_handler(exc, context)
    if response is not None:
        return error_response('Solicitud invalida.', status=response.status_code, code='request_error', details=response.data)

    return error_response('Error interno no controlado.', status=500, code='internal_error')
