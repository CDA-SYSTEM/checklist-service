"""
Mapper entre MongoEngine Documents y Domain Entities para Inspections.
"""

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
            labrado = LabradoMeasurementVO(
                minimum_mm=doc.labrado.minimum_mm,
                measured_at=doc.labrado.measured_at,
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

        return InspectionEntity(
            id=str(doc.id),
            plate=doc.plate,
            vehicle_id=doc.vehicle_id,
            client_id=doc.client_id,
            vehicle_type=doc.vehicle_type,
            inspection_datetime=doc.inspection_datetime,
            inspector_id=doc.inspector_id,
            status=doc.status,
            responses=[
                InspectionItemResponseEntity(
                    section_code=r.section_code,
                    subsection_code=r.subsection_code,
                    item_code=r.item_code,
                    response=r.response,
                    defect_type=r.defect_type or '',
                    observation=r.observation or '',
                )
                for r in doc.responses
            ],
            observations=doc.observations or '',
            general_result=doc.general_result,
            template_ref=template_ref,
            template_snapshot=doc.template_snapshot,
            labrado=labrado,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
