"""
Ports (interfaces) del bounded context Labrado.

Define el contrato que el adaptador de persistencia debe cumplir.
Labrado opera sobre la inspección pero a través de su propio port,
rompiendo el acoplamiento directo con InspectionRepository.
"""

from abc import ABC, abstractmethod

from apps.inspections.domain.entities import InspectionEntity, LabradoMeasurementVO


class LabradoRepositoryPort(ABC):
    """Port de salida — contrato para persistencia de mediciones de labrado."""

    @abstractmethod
    def get_inspection(self, inspection_id: str) -> InspectionEntity:
        ...

    @abstractmethod
    def save_labrado(
        self, inspection_id: str, labrado: LabradoMeasurementVO
    ) -> InspectionEntity:
        ...
