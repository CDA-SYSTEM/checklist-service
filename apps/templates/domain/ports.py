"""
Ports (interfaces) del bounded context Templates.

Define el contrato que cualquier adaptador de persistencia debe cumplir.
"""

from abc import ABC, abstractmethod

from apps.templates.domain.entities import TemplateEntity


class TemplateRepositoryPort(ABC):
    """Port de salida — contrato para persistencia de plantillas."""

    @abstractmethod
    def list_all(self) -> list[TemplateEntity]:
        ...

    @abstractmethod
    def list_by_vehicle_type(
        self, vehicle_type: str, *, active_only: bool = False
    ) -> list[TemplateEntity]:
        ...

    @abstractmethod
    def get_by_id(self, template_id: str) -> TemplateEntity:
        ...

    @abstractmethod
    def get_by_code_and_version(self, code: str, version: int) -> TemplateEntity | None:
        ...

    @abstractmethod
    def get_active_by_vehicle_type(self, vehicle_type: str) -> TemplateEntity:
        ...

    @abstractmethod
    def get_latest_version(self, code: str) -> TemplateEntity | None:
        ...

    @abstractmethod
    def deactivate_versions(self, code: str) -> None:
        ...

    @abstractmethod
    def create(self, entity: TemplateEntity) -> TemplateEntity:
        ...

    @abstractmethod
    def update(self, template_id: str, entity: TemplateEntity) -> TemplateEntity:
        ...

    @abstractmethod
    def delete(self, template_id: str) -> None:
        ...
