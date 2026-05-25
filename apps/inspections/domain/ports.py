"""
Ports (interfaces) del bounded context Inspections.

Define el contrato que cualquier adaptador de persistencia o validación
externa debe cumplir.
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

    @abstractmethod
    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        plate: str | None = None,
        status: str | None = None,
        vehicle_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[InspectionEntity], int]:
        """
        Retorna tupla (items, total_count) con paginación y filtros opcionales.
        """


class EntityExistencePort(ABC):
    """Port de salida — validación de existencia contra servicios externos."""

    @abstractmethod
    def assert_vehicle_exists(self, vehicle_id: int) -> None:
        ...

    @abstractmethod
    def assert_client_exists(self, client_id: int) -> None:
        ...


class InspectionEventPublisherPort(ABC):
    """Puerto de salida para la publicación de eventos de inspección."""

    @abstractmethod
    def publish_inspection_completed(self, inspection: InspectionEntity) -> None:
        ...
