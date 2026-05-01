"""
Entidades del bounded context Labrado.

Re-exporta los Value Objects definidos en inspections.domain.entities
porque el labrado es un sub-dominio que comparte estos VOs.
"""

from apps.inspections.domain.entities import (
    AxleMeasurementVO,
    LabradoMeasurementVO,
    TireMeasurementVO,
    WheelMeasurementVO,
)

__all__ = [
    'AxleMeasurementVO',
    'LabradoMeasurementVO',
    'TireMeasurementVO',
    'WheelMeasurementVO',
]
