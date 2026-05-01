"""
Factory de inyección de dependencias para Templates.

Único punto donde se conectan los Ports (ABCs) con los Adapters concretos.
"""

from apps.templates.adapters.driven.repository import MongoTemplateRepository
from apps.templates.application.use_cases import TemplateUseCases


def get_template_use_cases() -> TemplateUseCases:
    return TemplateUseCases(repository=MongoTemplateRepository())
