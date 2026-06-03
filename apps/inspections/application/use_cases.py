"""
Casos de uso del bounded context Inspections.

Depende SOLO de Ports (ABCs) y Entities (dataclasses).
Cero imports de infrastructure, documents, MongoEngine.
"""

from dataclasses import asdict
from datetime import UTC, datetime

from apps.common.domain.constants import GeneralResult, InspectionStatus, VehicleType
from apps.common.domain.exceptions import ConflictError, ValidationError
from apps.inspections.domain.entities import (
    InspectionEntity,
    InspectionItemResponseEntity,
    TemplateReferenceVO,
)
from apps.inspections.domain.ports import (
    EntityExistencePort,
    InspectionEventPublisherPort,
    InspectionRepositoryPort,
)
from apps.templates.domain.ports import TemplateRepositoryPort


class InspectionUseCases:
    """Orquesta las operaciones de negocio sobre inspecciones vehiculares."""

    def __init__(
        self,
        inspection_repository: InspectionRepositoryPort,
        template_repository: TemplateRepositoryPort,
        existence_validator: EntityExistencePort | None = None,
        event_publisher: InspectionEventPublisherPort | None = None,
    ):
        self.inspection_repository = inspection_repository
        self.template_repository = template_repository
        self.existence_validator = existence_validator
        self.event_publisher = event_publisher

    # ------------------------------------------------------------------
    # Resolución de templates (via port inyectado)
    # ------------------------------------------------------------------

    def _resolve_template(self, vehicle_type: str, template_id: str | None):
        if vehicle_type not in VehicleType.ALL:
            raise ValidationError('Tipo de vehiculo no valido.')

        if template_id:
            template = self.template_repository.get_by_id(template_id)
        else:
            template = self.template_repository.get_active_by_vehicle_type(
                vehicle_type
            )

        if vehicle_type not in template.supported_vehicle_types:
            raise ValidationError(
                'La plantilla no corresponde al tipo de vehiculo de la inspeccion.'
            )

        return template

    def _build_template_snapshot(self, template) -> dict:
        """Genera un snapshot serializable del template para la inspección."""
        return {
            'code': template.code,
            'name': template.name,
            'version': template.version,
            'supported_vehicle_types': template.supported_vehicle_types,
            'sections': [
                {
                    'code': s.code,
                    'title': s.title,
                    'order': s.order,
                    'subsections': [
                        {
                            'code': ss.code,
                            'title': ss.title,
                            'order': ss.order,
                            'items': [
                                {
                                    'code': i.code,
                                    'description': i.description,
                                    'defect_type': i.defect_type,
                                    'observation': i.observation,
                                    'order': i.order,
                                }
                                for i in ss.items
                            ],
                        }
                        for ss in s.subsections
                    ],
                }
                for s in template.sections
            ],
        }

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def list_inspections(self) -> list[InspectionEntity]:
        return self.inspection_repository.list_all()

    def get_inspection(self, inspection_id: str) -> InspectionEntity:
        return self.inspection_repository.get_by_id(inspection_id)

    def find_by_plate(self, plate: str) -> list[InspectionEntity]:
        return self.inspection_repository.by_plate(plate)

    def find_by_status(self, status: str) -> list[InspectionEntity]:
        if status not in InspectionStatus.ALL:
            raise ValidationError('Estado de inspeccion no valido.')
        return self.inspection_repository.by_status(status)

    def find_by_vehicle_id(self, vehicle_id: int) -> list[InspectionEntity]:
        return self.inspection_repository.by_vehicle_id(vehicle_id)

    def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[InspectionEntity]:
        if start_date > end_date:
            raise ValidationError('El rango de fechas es invalido.')
        return self.inspection_repository.by_date_range(start_date, end_date)

    def list_inspections_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        plate: str | None = None,
        status: str | None = None,
        vehicle_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[InspectionEntity], int]:
        if status and status not in InspectionStatus.ALL:
            raise ValidationError('Estado de inspeccion no valido.')
        if start_date and end_date and start_date > end_date:
            raise ValidationError('El rango de fechas es invalido.')
        return self.inspection_repository.get_paginated(
            page=page,
            page_size=page_size,
            plate=plate,
            status=status,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
        )

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def create_inspection(self, payload: dict) -> InspectionEntity:
        template = self._resolve_template(
            payload['vehicle_type'], payload.get('template_id')
        )

        if self.existence_validator:
            self.existence_validator.assert_vehicle_exists(payload['vehicle_id'])
            client_id = payload.get('client_id')
            if client_id is not None:
                self.existence_validator.assert_client_exists(client_id)

        entity = InspectionEntity(
            plate=payload['plate'].upper(),
            vehicle_id=payload['vehicle_id'],
            client_id=payload.get('client_id'),
            vehicle_type=payload['vehicle_type'],
            inspection_datetime=payload.get(
                'inspection_datetime', datetime.now(UTC)
            ),
            inspector_id=payload['inspector_id'],
            observations=payload.get('observations', ''),
            status=InspectionStatus.BORRADOR,
            template_ref=TemplateReferenceVO(
                template_id=str(template.id),
                code=template.code,
                version=template.version,
            ),
            template_snapshot=self._build_template_snapshot(template),
            responses=[
                InspectionItemResponseEntity(**r)
                for r in payload.get('responses', [])
            ],
        )
        return self.inspection_repository.create(entity)

    def update_inspection(
        self, inspection_id: str, payload: dict
    ) -> InspectionEntity:
        current = self.inspection_repository.get_by_id(inspection_id)

        updated_entity = InspectionEntity(
            id=inspection_id,
            plate=payload.get('plate', current.plate),
            vehicle_id=payload.get('vehicle_id', current.vehicle_id),
            client_id=payload.get('client_id', current.client_id),
            vehicle_type=current.vehicle_type,
            inspection_datetime=payload.get(
                'inspection_datetime', current.inspection_datetime
            ),
            inspector_id=payload.get('inspector_id', current.inspector_id),
            status=payload.get('status', current.status),
            observations=payload.get('observations', current.observations),
            general_result=payload.get('general_result', current.general_result),
            template_ref=current.template_ref,
            template_snapshot=current.template_snapshot,
            responses=[
                InspectionItemResponseEntity(**r)
                for r in payload.get('responses', [])
            ]
            if 'responses' in payload
            else current.responses,
            labrado=current.labrado,
        )
        return self.inspection_repository.update(inspection_id, updated_entity)

    def save_draft(
        self, inspection_id: str, payload: dict
    ) -> InspectionEntity:
        payload['status'] = InspectionStatus.BORRADOR
        return self.update_inspection(inspection_id, payload)

    def mark_in_progress(
        self, inspection_id: str, payload: dict
    ) -> InspectionEntity:
        payload['status'] = InspectionStatus.EN_PROGRESO
        return self.update_inspection(inspection_id, payload)

    def close_inspection(
        self, inspection_id: str, payload: dict
    ) -> InspectionEntity:
        current = self.inspection_repository.get_by_id(inspection_id)
        if current.status == InspectionStatus.CERRADA:
            raise ConflictError(
                'La inspeccion ya se encuentra cerrada.'
            )

        test_entity = InspectionEntity(
            responses=[
                InspectionItemResponseEntity(**r)
                for r in payload.get('responses', [])
            ]
            if 'responses' in payload
            else current.responses,
            labrado=current.labrado,
        )
        test_entity.validate_ready_for_close()

        payload['status'] = InspectionStatus.CERRADA
        closed_inspection = self.update_inspection(inspection_id, payload)
        if self.event_publisher:
            self.event_publisher.publish_inspection_completed(closed_inspection)
        return closed_inspection

    def get_stats(self) -> dict:
        inspections = self.inspection_repository.list_all()
        total = len(inspections)

        by_status = {}
        by_result = {}
        by_vehicle_type = {}
        today_count = 0
        month_count = 0
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        for insp in inspections:
            status = getattr(insp, 'status', 'UNKNOWN')
            by_status[status] = by_status.get(status, 0) + 1

            result = getattr(insp, 'general_result', None) or 'PENDIENTE'
            by_result[result] = by_result.get(result, 0) + 1

            vtype = getattr(insp, 'vehicle_type', 'UNKNOWN')
            by_vehicle_type[vtype] = by_vehicle_type.get(vtype, 0) + 1

            insp_date = getattr(insp, 'inspection_datetime', None)
            if insp_date:
                if isinstance(insp_date, datetime) and insp_date >= today_start:
                    today_count += 1
                if isinstance(insp_date, datetime) and insp_date >= month_start:
                    month_count += 1

        templates_count = 0
        try:
            from apps.templates.adapters.driven.documents import ChecklistTemplate
            templates_count = ChecklistTemplate.objects.count()
        except Exception:
            pass

        labrados_count = 0
        try:
            from apps.inspections.adapters.driven.documents import Inspection
            labrados_count = Inspection.objects(labrado__ne=None).count()
        except Exception:
            pass

        return {
            'total_inspections': total,
            'today_inspections': today_count,
            'month_inspections': month_count,
            'by_status': by_status,
            'by_result': by_result,
            'by_vehicle_type': by_vehicle_type,
            'total_templates': templates_count,
            'total_with_labrado': labrados_count,
        }

    def delete_inspection(self, inspection_id: str) -> dict:
        self.inspection_repository.delete(inspection_id)
        return {'id': inspection_id}
