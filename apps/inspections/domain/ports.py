"""
Ports (interfaces) del bounded context Inspections.

Define el contrato que cualquier adaptador de persistencia debe cumplir.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from apps.inspections.domain.entities import InspectionEntity


class InspectionRepositoryPort(ABC):
    """Port de salida — contrato para persistencia de inspecciones."""

    @abstractmethod
    def list_all(self) -> list[InspectionEntity]:
        ...

    @abstractmethod
    def get_by_id(self, inspection_id: str) -> InspectionEntity:
        ...

    @abstractmethod
    def create(self, entity: InspectionEntity) -> InspectionEntity:
        ...

    @abstractmethod
    def update(self, inspection_id: str, entity: InspectionEntity) -> InspectionEntity:
        ...

    @abstractmethod
    def delete(self, inspection_id: str) -> None:
        ...

    @abstractmethod
    def by_plate(self, plate: str) -> list[InspectionEntity]:
        ...

    @abstractmethod
    def by_status(self, status: str) -> list[InspectionEntity]:
        ...

    @abstractmethod
    def by_vehicle_id(self, vehicle_id: int) -> list[InspectionEntity]:
        ...

    @abstractmethod
    def by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[InspectionEntity]:
        ...
