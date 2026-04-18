from apps.common.domain.constants import TemplateCode, VehicleType
from apps.common.domain.exceptions import ValidationError
from apps.templates.infrastructure.repository import TemplateRepository


def _template_to_dict(template):
    return {
        'id': str(template.id),
        'code': template.code,
        'name': template.name,
        'version': template.version,
        'active': template.active,
        'supported_vehicle_types': template.supported_vehicle_types,
        'source_file': template.source_file,
        'sections': [
            {
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
                                'source_row': item.source_row,
                            }
                            for item in subsection.items
                        ],
                    }
                    for subsection in section.subsections
                ],
            }
            for section in template.sections
        ],
        'created_at': template.created_at,
        'updated_at': template.updated_at,
    }


class TemplateUseCases:
    def __init__(self, repository=None):
        self.repository = repository or TemplateRepository()

    def list_templates(self):
        return [_template_to_dict(t) for t in self.repository.list_templates()]

    def list_templates_by_vehicle_type(self, vehicle_type: str):
        if vehicle_type not in VehicleType.ALL:
            raise ValidationError('Tipo de vehiculo no valido.')
        templates = self.repository.list_by_vehicle_type(vehicle_type)
        return [_template_to_dict(t) for t in templates]

    def get_template(self, template_id: str):
        return _template_to_dict(self.repository.get_by_id(template_id))

    def get_active_template_by_vehicle_type(self, vehicle_type: str):
        if vehicle_type not in VehicleType.ALL:
            raise ValidationError('Tipo de vehiculo no valido.')
        return _template_to_dict(self.repository.get_active_by_vehicle_type(vehicle_type))

    def get_motos_template(self):
        templates = self.repository.list_by_vehicle_type(VehicleType.MOTO, active_only=True)
        template = templates.first()
        if not template:
            raise ValidationError('No hay plantilla activa para motos.')
        return _template_to_dict(template)

    def get_livianos_pesados_template(self):
        templates = self.repository.list_by_vehicle_type(VehicleType.LIVIANO, active_only=True)
        templates = templates.filter(supported_vehicle_types=VehicleType.PESADO)
        template = templates.first()
        if not template:
            raise ValidationError('No hay plantilla activa para livianos y pesados.')
        return _template_to_dict(template)

    def create_template(self, payload: dict):
        code = payload['code']
        requested_version = payload.get('version')

        if requested_version is None:
            latest = self.repository.get_latest_version(code)
            payload['version'] = 1 if latest is None else latest.version + 1

        if payload.get('active', True):
            self.repository.deactivate_versions(code)

        created = self.repository.create(payload)
        return _template_to_dict(created)

    def update_template(self, template_id: str, payload: dict):
        if payload.get('active'):
            code = payload.get('code')
            if code is None:
                current = self.repository.get_by_id(template_id)
                code = current.code
            self.repository.deactivate_versions(code)

        updated = self.repository.update(template_id, payload)
        return _template_to_dict(updated)

    def delete_template(self, template_id: str):
        self.repository.delete(template_id)
        return {'id': template_id}
