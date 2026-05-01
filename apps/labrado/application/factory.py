"""
Factory de inyección de dependencias para Labrado.

Único punto donde se conectan los Ports (ABCs) con los Adapters concretos.
"""

from apps.labrado.adapters.driven.repository import MongoLabradoRepository
from apps.labrado.application.use_cases import LabradoUseCases


def get_labrado_use_cases() -> LabradoUseCases:
    return LabradoUseCases(repository=MongoLabradoRepository())
