"""
Casos de uso del bounded context Labrado.

Depende SOLO de Ports (ABCs) y Domain Entities/Services.
Cero imports de infrastructure o repositorios de otros bounded contexts.
"""

from apps.common.domain.exceptions import ValidationError
from apps.inspections.domain.entities import InspectionEntity
from apps.labrado.domain.ports import LabradoRepositoryPort
from apps.labrado.domain.services import compute_labrado


class LabradoUseCases:
    """Orquesta las operaciones de negocio de mediciones de labrado."""

    def __init__(self, repository: LabradoRepositoryPort):
        self.repository = repository

    def upsert_labrado(
        self, inspection_id: str, axles: list[dict]
    ) -> dict:
        if not axles:
            raise ValidationError('Debe enviar al menos un eje de labrado.')

        # Verificar que la inspección existe
        self.repository.get_inspection(inspection_id)

        # Calcular labrado usando el Domain Service (lógica pura)
        labrado_vo = compute_labrado(axles)

        # Persistir via port
        updated_inspection = self.repository.save_labrado(
            inspection_id, labrado_vo
        )

        return self._build_labrado_response(updated_inspection)

    def get_labrado_by_inspection(self, inspection_id: str) -> dict:
        inspection = self.repository.get_inspection(inspection_id)
        return self._build_labrado_response(inspection)

    @staticmethod
    def _build_labrado_response(inspection: InspectionEntity) -> dict:
        """Construye la respuesta de labrado a partir de una InspectionEntity."""
        if inspection.labrado is None:
            return {
                'inspection_id': inspection.id,
                'labrado': None,
            }

        return {
            'inspection_id': inspection.id,
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
