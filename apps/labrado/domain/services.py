"""
Domain Service — Cálculo de profundidad de labrado.

Lógica pura de dominio sin dependencias de I/O, frameworks o persistencia.
Calcula los mínimos en cascada: neumático → rueda → eje → vehículo.
"""

from datetime import UTC, datetime

from apps.common.domain.exceptions import ValidationError
from apps.inspections.domain.entities import (
    AxleMeasurementVO,
    LabradoMeasurementVO,
    TireMeasurementVO,
    WheelMeasurementVO,
)


def compute_labrado(axles_data: list[dict]) -> LabradoMeasurementVO:
    """Calcula mediciones de labrado con mínimos en cascada.

    Soporta:
    - Motos: 1 eje, 2 llantas simples (delantera/trasera)
    - Livianos: 2 ejes + repuesto, llantas simples
    - Pesados: hasta 5 ejes + repuesto, llantas pachas (dobles) del eje 2 en adelante
    """
    computed_axles: list[AxleMeasurementVO] = []
    axle_minimums: list[float] = []

    for axle in axles_data:
        computed_wheels: list[WheelMeasurementVO] = []
        wheel_minimums: list[float] = []

        for wheel in axle['wheels']:
            computed_tires: list[TireMeasurementVO] = []
            tire_minimums: list[float] = []

            for tire in wheel['tires']:
                measures = [tire['outer_mm'], tire['middle_mm'], tire['inner_mm']]
                if any(value < 0 for value in measures):
                    raise ValidationError('Las medidas de labrado no pueden ser negativas.')

                minimum = min(measures)
                tire_minimums.append(minimum)
                computed_tires.append(
                    TireMeasurementVO(
                        tire_code=tire['tire_code'],
                        outer_mm=tire['outer_mm'],
                        middle_mm=tire['middle_mm'],
                        inner_mm=tire['inner_mm'],
                        minimum_mm=minimum,
                    )
                )

            wheel_minimum = min(tire_minimums) if tire_minimums else 0.0
            wheel_minimums.append(wheel_minimum)
            computed_wheels.append(
                WheelMeasurementVO(
                    wheel_code=wheel['wheel_code'],
                    minimum_mm=wheel_minimum,
                    tires=computed_tires,
                )
            )

        axle_minimum = min(wheel_minimums) if wheel_minimums else 0.0
        axle_minimums.append(axle_minimum)
        computed_axles.append(
            AxleMeasurementVO(
                axle_code=axle['axle_code'],
                minimum_mm=axle_minimum,
                wheels=computed_wheels,
            )
        )

    return LabradoMeasurementVO(
        axles=computed_axles,
        minimum_mm=min(axle_minimums) if axle_minimums else 0.0,
        measured_at=datetime.now(UTC),
    )
