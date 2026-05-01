"""
Entidades de dominio del bounded context Templates.

Dataclasses puras de Python — sin dependencias de frameworks externos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TemplateItemEntity:
    """Ítem individual dentro de una subsección de checklist."""

    code: str
    description: str
    defect_type: str
    observation: str = ''
    order: int = 0


@dataclass
class TemplateSubsectionEntity:
    """Subsección que agrupa ítems de inspección."""

    code: str
    title: str
    order: int = 0
    items: list[TemplateItemEntity] = field(default_factory=list)


@dataclass
class TemplateSectionEntity:
    """Sección principal de una plantilla de checklist."""

    code: str
    title: str
    order: int = 0
    subsections: list[TemplateSubsectionEntity] = field(default_factory=list)


@dataclass
class TemplateEntity:
    """Entidad raíz — plantilla de checklist versionada."""

    id: str | None = None
    code: str = ''
    name: str = ''
    version: int = 1
    active: bool = True
    supported_vehicle_types: list[str] = field(default_factory=list)
    sections: list[TemplateSectionEntity] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
