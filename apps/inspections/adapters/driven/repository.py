"""
Driven Adapter — Implementación MongoDB del InspectionRepositoryPort.
"""

from datetime import datetime

from apps.common.domain.exceptions import NotFoundError
from apps.inspections.adapters.driven.documents import Inspection, LabradoMeasurement, InspectionItemResponse
from apps.inspections.adapters.driven.mappers import InspectionMapper
from apps.inspections.domain.entities import InspectionEntity
from apps.inspections.domain.ports import InspectionRepositoryPort


class MongoInspectionRepository(InspectionRepositoryPort):
    """Driven adapter — implementa InspectionRepositoryPort con MongoDB."""

    def list_all(self) -> list[InspectionEntity]:
        docs = Inspection.objects.order_by('-inspection_datetime')
        return [InspectionMapper.to_entity(d) for d in docs]

    def get_by_id(self, inspection_id: str) -> InspectionEntity:
        doc = Inspection.objects(id=inspection_id).first()
        if not doc:
            raise NotFoundError('Inspeccion no encontrada.')
        return InspectionMapper.to_entity(doc)

    def create(self, entity: InspectionEntity) -> InspectionEntity:
        doc = Inspection(
            plate=entity.plate,
            vehicle_id=entity.vehicle_id,
            client_id=entity.client_id,
            vehicle_type=entity.vehicle_type,
            inspection_datetime=entity.inspection_datetime,
            inspector_id=entity.inspector_id,
            status=entity.status,
            observations=entity.observations,
            template_ref=entity.template_ref.__dict__ if entity.template_ref else None,
            template_snapshot=entity.template_snapshot or {},
        )
        if entity.responses:
            doc.responses = [r.__dict__ for r in entity.responses]
        doc.save()
        return InspectionMapper.to_entity(doc)

    def update(self, inspection_id: str, entity: InspectionEntity) -> InspectionEntity:
        doc = Inspection.objects(id=inspection_id).first()
        if not doc:
            raise NotFoundError('Inspeccion no encontrada.')

        updatable_fields = {
            'plate': entity.plate,
            'vehicle_id': entity.vehicle_id,
            'client_id': entity.client_id,
            'inspection_datetime': entity.inspection_datetime,
            'inspector_id': entity.inspector_id,
            'observations': entity.observations,
            'status': entity.status,
            'general_result': entity.general_result,
        }
        for key, value in updatable_fields.items():
            if value is not None:
                setattr(doc, key, value)

        doc.responses = [
            InspectionItemResponse(
                section_code=r.section_code,
                subsection_code=r.subsection_code,
                item_code=r.item_code,
                response=r.response,
                defect_type=r.defect_type,
                observation=r.observation
            )
            for r in entity.responses
        ]

        if entity.labrado:
            from apps.inspections.adapters.driven.documents import (
                AxleMeasurement,
                TireMeasurement,
                WheelMeasurement,
            )

            doc.labrado = LabradoMeasurement(
                minimum_mm=entity.labrado.minimum_mm,
                measured_at=entity.labrado.measured_at,
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
                    for a in entity.labrado.axles
                ],
            )

        doc.save()
        return InspectionMapper.to_entity(doc)

    def delete(self, inspection_id: str) -> None:
        doc = Inspection.objects(id=inspection_id).first()
        if not doc:
            raise NotFoundError('Inspeccion no encontrada.')
        doc.delete()

    def by_plate(self, plate: str) -> list[InspectionEntity]:
        docs = Inspection.objects(plate__iexact=plate).order_by('-inspection_datetime')
        return [InspectionMapper.to_entity(d) for d in docs]

    def by_status(self, status: str) -> list[InspectionEntity]:
        docs = Inspection.objects(status=status).order_by('-inspection_datetime')
        return [InspectionMapper.to_entity(d) for d in docs]

    def by_vehicle_id(self, vehicle_id: int) -> list[InspectionEntity]:
        docs = Inspection.objects(vehicle_id=vehicle_id).order_by('-inspection_datetime')
        return [InspectionMapper.to_entity(d) for d in docs]

    def by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[InspectionEntity]:
        docs = Inspection.objects(
            inspection_datetime__gte=start_date,
            inspection_datetime__lte=end_date,
        ).order_by('-inspection_datetime')
        return [InspectionMapper.to_entity(d) for d in docs]
