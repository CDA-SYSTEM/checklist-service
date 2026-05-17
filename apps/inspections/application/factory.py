"""
Factory de inyección de dependencias para Inspections.

Único punto donde se conectan los Ports (ABCs) con los Adapters concretos.
"""

from django.conf import settings

from apps.inspections.adapters.driven.existence_validator import (
    RabbitMQExistenceValidator,
)
from apps.inspections.adapters.driven.repository import MongoInspectionRepository
from apps.inspections.application.use_cases import InspectionUseCases
from apps.templates.adapters.driven.repository import MongoTemplateRepository


def get_inspection_use_cases() -> InspectionUseCases:
    rabbitmq_url = getattr(settings, "RABBITMQ_URI", None) or None
    if rabbitmq_url:
        existence_validator = RabbitMQExistenceValidator(
            rabbitmq_url=rabbitmq_url,
            client_queue=getattr(settings, "RABBITMQ_CLIENT_QUEUE", "client-service-queue"),
            vehicle_queue=getattr(settings, "RABBITMQ_VEHICLE_QUEUE", "vehicle-service-queue"),
            timeout_ms=getattr(settings, "RABBITMQ_RPC_TIMEOUT_MS", 8000),
        )
    else:
        existence_validator = None

    return InspectionUseCases(
        inspection_repository=MongoInspectionRepository(),
        template_repository=MongoTemplateRepository(),
        existence_validator=existence_validator,
    )
