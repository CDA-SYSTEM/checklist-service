"""
Casos de uso del bounded context Templates.

Depende SOLO de Ports (ABCs) y Entities (dataclasses).
Cero imports de infrastructure, documents, MongoEngine.
"""

from dataclasses import asdict

from apps.common.domain.constants import VehicleType
from apps.common.domain.exceptions import NotFoundError, ValidationError
from apps.templates.domain.entities import (
    TemplateEntity,
    TemplateItemEntity,
    TemplateSectionEntity,
    TemplateSubsectionEntity,
)
from apps.templates.domain.ports import TemplateRepositoryPort


class TemplateUseCases:
    """Orquesta las operaciones de negocio sobre plantillas de checklist."""

    def __init__(self, repository: TemplateRepositoryPort):
        self.repository = repository

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def list_templates(self) -> list[TemplateEntity]:
        return self.repository.list_all()

    def list_templates_by_vehicle_type(
        self, vehicle_type: str
    ) -> list[TemplateEntity]:
        if vehicle_type not in VehicleType.ALL:
            raise ValidationError('Tipo de vehiculo no valido.')
        return self.repository.list_by_vehicle_type(vehicle_type)

    def get_template(self, template_id: str) -> TemplateEntity:
        return self.repository.get_by_id(template_id)

    def get_active_template_by_vehicle_type(
        self, vehicle_type: str
    ) -> TemplateEntity:
        if vehicle_type not in VehicleType.ALL:
            raise ValidationError('Tipo de vehiculo no valido.')
        return self.repository.get_active_by_vehicle_type(vehicle_type)

    def get_motos_template(self) -> TemplateEntity:
        templates = self.repository.list_by_vehicle_type(
            VehicleType.MOTO, active_only=True
        )
        if not templates:
            raise NotFoundError('No hay plantilla activa para motos.')
        return templates[0]

    def get_livianos_pesados_template(self) -> TemplateEntity:
        templates = self.repository.list_by_vehicle_type(
            VehicleType.LIVIANO, active_only=True
        )
        # Filtrar solo las que también soportan PESADO
        combined = [
            t for t in templates if VehicleType.PESADO in t.supported_vehicle_types
        ]
        if not combined:
            raise NotFoundError('No hay plantilla activa para livianos y pesados.')
        return combined[0]

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def create_template(self, payload: dict) -> TemplateEntity:
        code = payload['code']
        requested_version = payload.get('version')

        if requested_version is None:
            latest = self.repository.get_latest_version(code)
            version = 1 if latest is None else latest.version + 1
        else:
            version = requested_version

        if payload.get('active', True):
            self.repository.deactivate_versions(code)

        entity = TemplateEntity(
            code=code,
            name=payload['name'],
            version=version,
            active=payload.get('active', True),
            supported_vehicle_types=payload.get('supported_vehicle_types', []),
            sections=self._build_sections(payload.get('sections', [])),
        )
        return self.repository.create(entity)

    def update_template(
        self, template_id: str, payload: dict
    ) -> TemplateEntity:
        current = self.repository.get_by_id(template_id)

        if payload.get('active'):
            code = payload.get('code', current.code)
            self.repository.deactivate_versions(code)

        updated_entity = TemplateEntity(
            id=template_id,
            code=payload.get('code', current.code),
            name=payload.get('name', current.name),
            version=current.version,
            active=payload.get('active', current.active),
            supported_vehicle_types=payload.get(
                'supported_vehicle_types', current.supported_vehicle_types
            ),
            sections=self._build_sections(payload.get('sections'))
            if 'sections' in payload
            else current.sections,
        )
        return self.repository.update(template_id, updated_entity)

    def delete_template(self, template_id: str) -> dict:
        self.repository.delete(template_id)
        return {'id': template_id}

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    @staticmethod
    def _build_sections(
        sections_data: list[dict] | None,
    ) -> list[TemplateSectionEntity]:
        if not sections_data:
            return []
        return [
            TemplateSectionEntity(
                code=s.get('code', ''),
                title=s.get('title', ''),
                order=s.get('order', 0),
                subsections=[
                    TemplateSubsectionEntity(
                        code=ss.get('code', ''),
                        title=ss.get('title', ''),
                        order=ss.get('order', 0),
                        items=[
                            TemplateItemEntity(
                                code=i.get('code', ''),
                                description=i.get('description', ''),
                                defect_type=i.get('defect_type', ''),
                                observation=i.get('observation', ''),
                                order=i.get('order', 0),
                            )
                            for i in ss.get('items', [])
                        ],
                    )
                    for ss in s.get('subsections', [])
                ],
            )
            for s in sections_data
        ]
