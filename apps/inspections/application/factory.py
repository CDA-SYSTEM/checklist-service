"""
Factory de inyección de dependencias para Inspections.

Único punto donde se conectan los Ports (ABCs) con los Adapters concretos.
"""

from apps.inspections.adapters.driven.repository import MongoInspectionRepository
from apps.inspections.application.use_cases import InspectionUseCases
from apps.templates.adapters.driven.repository import MongoTemplateRepository


def get_inspection_use_cases() -> InspectionUseCases:
    return InspectionUseCases(
        inspection_repository=MongoInspectionRepository(),
        template_repository=MongoTemplateRepository(),
    )
