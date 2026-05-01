"""
Driven Adapter — Implementación MongoDB del LabradoRepositoryPort.

Opera sobre la colección 'inspections' pero expone solo la interfaz
que el bounded context Labrado necesita.
"""

from apps.common.domain.exceptions import NotFoundError
from apps.inspections.adapters.driven.documents import (
    AxleMeasurement,
    Inspection,
    LabradoMeasurement,
    TireMeasurement,
    WheelMeasurement,
)
from apps.inspections.adapters.driven.mappers import InspectionMapper
from apps.inspections.domain.entities import InspectionEntity, LabradoMeasurementVO
from apps.labrado.domain.ports import LabradoRepositoryPort


class MongoLabradoRepository(LabradoRepositoryPort):
    """Driven adapter — persiste labrado dentro del documento Inspection."""

    def get_inspection(self, inspection_id: str) -> InspectionEntity:
        doc = Inspection.objects(id=inspection_id).first()
        if not doc:
            raise NotFoundError('Inspeccion no encontrada.')
        return InspectionMapper.to_entity(doc)

    def save_labrado(
        self, inspection_id: str, labrado: LabradoMeasurementVO
    ) -> InspectionEntity:
        doc = Inspection.objects(id=inspection_id).first()
        if not doc:
            raise NotFoundError('Inspeccion no encontrada.')

        doc.labrado = LabradoMeasurement(
            minimum_mm=labrado.minimum_mm,
            measured_at=labrado.measured_at,
            axles=[
                AxleMeasurement(
                    axle_code=a.axle_code,
                    minimum_mm=a.minimum_mm,
                    wheels=[
                        WheelMeasurement(
                            wheel_code=w.wheel_code,
                            minimum_mm=w.minimum_mm,
                            tires=[
                                TireMeasurement(
                                    tire_code=t.tire_code,
                                    outer_mm=t.outer_mm,
                                    middle_mm=t.middle_mm,
                                    inner_mm=t.inner_mm,
                                    minimum_mm=t.minimum_mm,
                                )
                                for t in w.tires
                            ],
                        )
                        for w in a.wheels
                    ],
                )
                for a in labrado.axles
            ],
        )
        doc.save()
        return InspectionMapper.to_entity(doc)
