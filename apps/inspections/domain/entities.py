"""
Entidades y Value Objects del bounded context Inspections.

Dataclasses puras de Python — sin dependencias de frameworks externos.
Incluye los VOs de labrado porque están embebidos en Inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from apps.common.domain.exceptions import ValidationError

# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TemplateReferenceVO:
    """Referencia inmutable a la plantilla usada en una inspección."""

    template_id: str
    code: str
    version: int


@dataclass
class InspectionItemResponseEntity:
    """Respuesta individual a un ítem del checklist."""

    section_code: str
    subsection_code: str
    item_code: str
    response: str
    defect_type: str | None = None
    observation: str = ''


# ---------------------------------------------------------------------------
# Value Objects — Labrado (mediciones de profundidad de neumáticos)
# ---------------------------------------------------------------------------

@dataclass
class TireMeasurementVO:
    """Medición de un neumático individual (3 puntos + mínimo calculado)."""

    tire_code: str
    outer_mm: float
    middle_mm: float
    inner_mm: float
    minimum_mm: float = 0.0


@dataclass
class WheelMeasurementVO:
    """Posición de rueda con sus neumáticos (1 para simple, 2 para pacha)."""

    wheel_code: str
    minimum_mm: float = 0.0
    tires: list[TireMeasurementVO] = field(default_factory=list)


@dataclass
class AxleMeasurementVO:
    """Eje del vehículo con sus ruedas izquierda/derecha."""

    axle_code: str
    minimum_mm: float = 0.0
    wheels: list[WheelMeasurementVO] = field(default_factory=list)


@dataclass
class LabradoMeasurementVO:
    """Conjunto completo de mediciones de labrado de una inspección."""

    minimum_mm: float = 0.0
    measured_at: datetime | None = None
    axles: list[AxleMeasurementVO] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Entidad raíz — Inspección
# ---------------------------------------------------------------------------

@dataclass
class InspectionEntity:
    """Entidad raíz — inspección vehicular con checklist y labrado."""

    id: str | None = None
    plate: str = ''
    vehicle_id: int = 0
    client_id: int | None = None
    vehicle_type: str = ''
    inspection_datetime: datetime | None = None
    inspector_id: str = ''
    status: str = ''
    responses: list[InspectionItemResponseEntity] = field(default_factory=list)
    observations: str = ''
    general_result: str | None = None
    template_ref: TemplateReferenceVO | None = None
    template_snapshot: dict | None = None
    labrado: LabradoMeasurementVO | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def validate_ready_for_close(self) -> None:
        """
        Valida que la inspección cumpla los requisitos mínimos para cerrarse.
        """
        if not self.responses:
            raise ValidationError("La inspección debe tener el registro de las respuestas para ser cerrada.")
        if not self.labrado:
            raise ValidationError("La inspección debe tener el registro de labrado para ser cerrada.")
