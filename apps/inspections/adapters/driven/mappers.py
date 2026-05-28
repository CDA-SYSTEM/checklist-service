"""
Mapper entre MongoEngine Documents y Domain Entities para Inspections.
"""

from datetime import timezone
from apps.inspections.adapters.driven.documents import Inspection
from apps.inspections.domain.entities import (
    AxleMeasurementVO,
    InspectionEntity,
    InspectionItemResponseEntity,
    LabradoMeasurementVO,
    TemplateReferenceVO,
    TireMeasurementVO,
    WheelMeasurementVO,
)


class InspectionMapper:
    """Convierte entre Document (persistencia) y Entity (dominio)."""

    @staticmethod
    def to_entity(doc: Inspection) -> InspectionEntity:
        labrado = None
        if doc.labrado:
            measured_at_dt = doc.labrado.measured_at
            if measured_at_dt and measured_at_dt.tzinfo is None:
                measured_at_dt = measured_at_dt.replace(tzinfo=timezone.utc)
                
            labrado = LabradoMeasurementVO(
                minimum_mm=doc.labrado.minimum_mm,
                measured_at=measured_at_dt,
                axles=[
                    AxleMeasurementVO(
                        axle_code=axle.axle_code,
                        minimum_mm=axle.minimum_mm,
                        wheels=[
                            WheelMeasurementVO(
                                wheel_code=wheel.wheel_code,
                                minimum_mm=wheel.minimum_mm,
                                tires=[
                                    TireMeasurementVO(
                                        tire_code=tire.tire_code,
                                        outer_mm=tire.outer_mm,
                                        middle_mm=tire.middle_mm,
                                        inner_mm=tire.inner_mm,
                                        minimum_mm=tire.minimum_mm,
                                    )
                                    for tire in wheel.tires
                                ],
                            )
                            for wheel in axle.wheels
                        ],
                    )
                    for axle in doc.labrado.axles
                ],
            )

        template_ref = None
        if doc.template_ref:
            template_ref = TemplateReferenceVO(
                template_id=doc.template_ref.template_id,
                code=doc.template_ref.code,
                version=doc.template_ref.version,
            )

        inspection_datetime = doc.inspection_datetime
        if inspection_datetime and inspection_datetime.tzinfo is None:
            inspection_datetime = inspection_datetime.replace(tzinfo=timezone.utc)

        created_at = doc.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        updated_at = doc.updated_at
        if updated_at and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        return InspectionEntity(
            id=str(doc.id),
            plate=doc.plate,
            vehicle_id=doc.vehicle_id,
            client_id=doc.client_id,
            vehicle_type=doc.vehicle_type,
            inspection_datetime=inspection_datetime,
            inspector_id=doc.inspector_id,
            status=doc.status,
            responses=[
                InspectionItemResponseEntity(
                    section_code=r.section_code,
                    subsection_code=r.subsection_code,
                    item_code=r.item_code,
                    response=r.response,
                    defect_type=r.defect_type,
                    observation=r.observation or '',
                )
                for r in doc.responses
            ],
            observations=doc.observations or '',
            general_result=doc.general_result,
            template_ref=template_ref,
            template_snapshot=doc.template_snapshot,
            labrado=labrado,
            created_at=created_at,
            updated_at=updated_at,
        )
