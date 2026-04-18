from datetime import UTC, datetime

from apps.common.domain.constants import GeneralResult, InspectionStatus, VehicleType
from apps.common.domain.exceptions import ConflictError, ValidationError
from apps.inspections.infrastructure.repository import InspectionRepository
from apps.templates.infrastructure.documents import ChecklistTemplate


def _section_to_dict(section):
    return {
        'code': section.code,
        'title': section.title,
        'order': section.order,
        'subsections': [
            {
                'code': subsection.code,
                'title': subsection.title,
                'order': subsection.order,
                'items': [
                    {
                        'code': item.code,
                        'description': item.description,
                        'defect_type': item.defect_type,
                        'observation': item.observation,
                        'order': item.order,
                    }
                    for item in subsection.items
                ],
            }
            for subsection in section.subsections
        ],
    }


def _inspection_to_dict(inspection):
    labrado_data = None
    if inspection.labrado:
        labrado_data = {
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
        }

    return {
        'id': str(inspection.id),
        'plate': inspection.plate,
        'vehicle_id': inspection.vehicle_id,
        'client_id': inspection.client_id,
        'vehicle_type': inspection.vehicle_type,
        'inspection_datetime': inspection.inspection_datetime,
        'operators': inspection.operators,
        'status': inspection.status,
        'responses': [
            {
                'section_code': item.section_code,
                'subsection_code': item.subsection_code,
                'item_code': item.item_code,
                'response': item.response,
                'defect_type': item.defect_type,
                'observation': item.observation,
            }
            for item in inspection.responses
        ],
        'observations': inspection.observations,
        'general_result': inspection.general_result,
        'template_ref': {
            'template_id': inspection.template_ref.template_id,
            'code': inspection.template_ref.code,
            'version': inspection.template_ref.version,
        },
        'template_snapshot': inspection.template_snapshot,
        'labrado': labrado_data,
        'created_at': inspection.created_at,
        'updated_at': inspection.updated_at,
    }


class InspectionUseCases:
    def __init__(self, repository=None):
        self.repository = repository or InspectionRepository()

    def _resolve_template(self, vehicle_type: str, template_id: str | None):
        if vehicle_type not in VehicleType.ALL:
            raise ValidationError('Tipo de vehiculo no valido.')

        if template_id:
            template = ChecklistTemplate.objects(id=template_id).first()
            if not template:
                raise ValidationError('El template_id no existe.')
        else:
            template = (
                ChecklistTemplate.objects(supported_vehicle_types=vehicle_type, active=True)
                .order_by('-version')
                .first()
            )
            if not template:
                raise ValidationError('No existe plantilla activa para ese tipo de vehiculo.')

        if vehicle_type not in template.supported_vehicle_types:
            raise ValidationError('La plantilla no corresponde al tipo de vehiculo de la inspeccion.')

        return template

    def _prepare_template_payload(self, template):
        return {
            'template_ref': {
                'template_id': str(template.id),
                'code': template.code,
                'version': template.version,
            },
            'template_snapshot': {
                'code': template.code,
                'name': template.name,
                'version': template.version,
                'supported_vehicle_types': template.supported_vehicle_types,
                'sections': [_section_to_dict(section) for section in template.sections],
            },
        }

    def list_inspections(self):
        return [_inspection_to_dict(i) for i in self.repository.list_all()]

    def get_inspection(self, inspection_id: str):
        return _inspection_to_dict(self.repository.get_by_id(inspection_id))

    def create_inspection(self, payload: dict):
        template = self._resolve_template(payload['vehicle_type'], payload.get('template_id'))
        template_payload = self._prepare_template_payload(template)

        create_payload = {
            'plate': payload['plate'].upper(),
            'vehicle_id': payload['vehicle_id'],
            'client_id': payload.get('client_id', ''),
            'vehicle_type': payload['vehicle_type'],
            'inspection_datetime': payload.get('inspection_datetime', datetime.now(UTC)),
            'operators': payload.get('operators', []),
            'responses': payload.get('responses', []),
            'observations': payload.get('observations', ''),
            'status': InspectionStatus.BORRADOR,
            **template_payload,
        }

        created = self.repository.create(create_payload)
        return _inspection_to_dict(created)

    def update_inspection(self, inspection_id: str, payload: dict):
        current = self.repository.get_by_id(inspection_id)
        if current.status == InspectionStatus.CERRADA:
            raise ConflictError('La inspeccion esta cerrada y no puede modificarse.')

        updated = self.repository.update(inspection_id, payload)
        return _inspection_to_dict(updated)

    def save_draft(self, inspection_id: str, payload: dict):
        payload['status'] = InspectionStatus.BORRADOR
        updated = self.update_inspection(inspection_id, payload)
        return updated

    def mark_in_progress(self, inspection_id: str, payload: dict):
        payload['status'] = InspectionStatus.EN_PROGRESO
        updated = self.update_inspection(inspection_id, payload)
        return updated

    def close_inspection(self, inspection_id: str, payload: dict):
        if payload.get('general_result') not in GeneralResult.ALL:
            raise ValidationError('Debe indicar resultado_general valido para cerrar la inspeccion.')

        payload['status'] = InspectionStatus.CERRADA
        updated = self.update_inspection(inspection_id, payload)
        return updated

    def delete_inspection(self, inspection_id: str):
        self.repository.delete(inspection_id)
        return {'id': inspection_id}

    def find_by_plate(self, plate: str):
        return [_inspection_to_dict(i) for i in self.repository.by_plate(plate)]

    def find_by_status(self, status: str):
        if status not in InspectionStatus.ALL:
            raise ValidationError('Estado de inspeccion no valido.')
        return [_inspection_to_dict(i) for i in self.repository.by_status(status)]

    def find_by_vehicle_id(self, vehicle_id: str):
        return [_inspection_to_dict(i) for i in self.repository.by_vehicle_id(vehicle_id)]

    def find_by_date_range(self, start_date, end_date):
        if start_date > end_date:
            raise ValidationError('El rango de fechas es invalido.')
        return [_inspection_to_dict(i) for i in self.repository.by_date_range(start_date, end_date)]
