from datetime import UTC, datetime

from apps.common.domain.exceptions import ValidationError
from apps.inspections.infrastructure.repository import InspectionRepository


def _compute_labrado(axles: list[dict]):
    computed_axles = []
    axle_minimums = []

    for axle in axles:
        computed_wheels = []
        wheel_minimums = []

        for wheel in axle['wheels']:
            computed_tires = []
            tire_minimums = []

            for tire in wheel['tires']:
                measures = [tire['outer_mm'], tire['middle_mm'], tire['inner_mm']]
                if any(value < 0 for value in measures):
                    raise ValidationError('Las medidas de labrado no pueden ser negativas.')

                minimum = min(measures)
                tire_minimums.append(minimum)
                computed_tires.append(
                    {
                        'tire_code': tire['tire_code'],
                        'outer_mm': tire['outer_mm'],
                        'middle_mm': tire['middle_mm'],
                        'inner_mm': tire['inner_mm'],
                        'minimum_mm': minimum,
                    }
                )

            wheel_minimum = min(tire_minimums) if tire_minimums else 0
            wheel_minimums.append(wheel_minimum)
            computed_wheels.append(
                {
                    'wheel_code': wheel['wheel_code'],
                    'minimum_mm': wheel_minimum,
                    'tires': computed_tires,
                }
            )

        axle_minimum = min(wheel_minimums) if wheel_minimums else 0
        axle_minimums.append(axle_minimum)
        computed_axles.append(
            {
                'axle_code': axle['axle_code'],
                'minimum_mm': axle_minimum,
                'wheels': computed_wheels,
            }
        )

    return {
        'axles': computed_axles,
        'minimum_mm': min(axle_minimums) if axle_minimums else 0,
        'measured_at': datetime.now(UTC),
    }


class LabradoUseCases:
    def __init__(self, inspection_repository=None):
        self.inspection_repository = inspection_repository or InspectionRepository()

    def upsert_labrado(self, inspection_id: str, axles: list[dict]):
        if not axles:
            raise ValidationError('Debe enviar al menos un eje de labrado.')

        self.inspection_repository.get_by_id(inspection_id)
        labrado_payload = _compute_labrado(axles)

        updated = self.inspection_repository.update(inspection_id, {'labrado': labrado_payload})
        return self.get_labrado_by_inspection(str(updated.id))

    def get_labrado_by_inspection(self, inspection_id: str):
        inspection = self.inspection_repository.get_by_id(inspection_id)
        if inspection.labrado is None:
            return {
                'inspection_id': str(inspection.id),
                'labrado': None,
            }

        return {
            'inspection_id': str(inspection.id),
            'labrado': {
                'minimum_mm': inspection.labrado.minimum_mm,
                'measured_at': inspection.labrado.measured_at,
                'axles': [
                    {
                        'axle_code': axle.axle_code,
                        'minimum_mm': axle.minimum_mm,
                        'wheels': [
                            {
                                'wheel_code': wheel.wheel_code,
                                'minimum_mm': wheel.minimum_mm,
                                'tires': [
                                    {
                                        'tire_code': tire.tire_code,
                                        'outer_mm': tire.outer_mm,
                                        'middle_mm': tire.middle_mm,
                                        'inner_mm': tire.inner_mm,
                                        'minimum_mm': tire.minimum_mm,
                                    }
                                    for tire in wheel.tires
                                ],
                            }
                            for wheel in axle.wheels
                        ],
                    }
                    for axle in inspection.labrado.axles
                ],
            },
        }
