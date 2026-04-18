from mongoengine.errors import NotUniqueError

from apps.common.domain.exceptions import ConflictError, NotFoundError, ValidationError
from apps.templates.infrastructure.documents import (
    ChecklistTemplate,
    TemplateItem,
    TemplateSection,
    TemplateSubsection,
)


def _build_template_items(items_payload):
    if items_payload is None:
        return []
    if not isinstance(items_payload, list):
        raise ValidationError('El campo items de una subseccion debe ser una lista.')

    built_items = []
    for item in items_payload:
        if isinstance(item, TemplateItem):
            built_items.append(item)
            continue
        if not isinstance(item, dict):
            raise ValidationError('Cada item de subseccion debe ser un objeto valido.')

        built_items.append(
            TemplateItem(
                code=item.get('code'),
                description=item.get('description'),
                defect_type=item.get('defect_type'),
                observation=item.get('observation', ''),
                order=item.get('order'),
                source_row=item.get('source_row'),
            )
        )

    return built_items


def _build_template_subsections(subsections_payload):
    if subsections_payload is None:
        return []
    if not isinstance(subsections_payload, list):
        raise ValidationError('El campo subsections de una seccion debe ser una lista.')

    built_subsections = []
    for subsection in subsections_payload:
        if isinstance(subsection, TemplateSubsection):
            built_subsections.append(subsection)
            continue
        if not isinstance(subsection, dict):
            raise ValidationError('Cada subseccion debe ser un objeto valido.')

        built_subsections.append(
            TemplateSubsection(
                code=subsection.get('code'),
                title=subsection.get('title'),
                order=subsection.get('order'),
                items=_build_template_items(subsection.get('items', [])),
            )
        )

    return built_subsections


def _build_template_sections(sections_payload):
    if sections_payload is None:
        return []
    if not isinstance(sections_payload, list):
        raise ValidationError('El campo sections debe ser una lista.')

    built_sections = []
    for section in sections_payload:
        if isinstance(section, TemplateSection):
            built_sections.append(section)
            continue
        if not isinstance(section, dict):
            raise ValidationError('Cada seccion debe ser un objeto valido.')

        built_sections.append(
            TemplateSection(
                code=section.get('code'),
                title=section.get('title'),
                order=section.get('order'),
                subsections=_build_template_subsections(section.get('subsections', [])),
            )
        )

    return built_sections


def _normalize_template_payload(payload: dict):
    normalized = dict(payload)
    if 'sections' in normalized:
        normalized['sections'] = _build_template_sections(normalized.get('sections'))
    return normalized


class TemplateRepository:
    def list_templates(self):
        return ChecklistTemplate.objects.order_by('-updated_at')

    def list_by_vehicle_type(self, vehicle_type: str, *, active_only: bool = False):
        query = ChecklistTemplate.objects.filter(supported_vehicle_types=vehicle_type)
        if active_only:
            query = query.filter(active=True)
        return query.order_by('-version')

    def get_by_id(self, template_id: str):
        template = ChecklistTemplate.objects(id=template_id).first()
        if not template:
            raise NotFoundError('Plantilla no encontrada.')
        return template

    def get_by_code_and_version(self, code: str, version: int):
        return ChecklistTemplate.objects(code=code, version=version).first()

    def get_active_by_vehicle_type(self, vehicle_type: str):
        template = (
            ChecklistTemplate.objects(supported_vehicle_types=vehicle_type, active=True)
            .order_by('-version')
            .first()
        )
        if not template:
            raise NotFoundError('No existe plantilla activa para el tipo de vehiculo solicitado.')
        return template

    def get_latest_version(self, code: str):
        return ChecklistTemplate.objects(code=code).order_by('-version').first()

    def deactivate_versions(self, code: str):
        ChecklistTemplate.objects(code=code, active=True).update(active=False)

    def create(self, payload: dict):
        payload = _normalize_template_payload(payload)
        try:
            template = ChecklistTemplate(**payload)
            template.save()
            return template
        except NotUniqueError as exc:
            raise ConflictError('Ya existe una plantilla con el mismo codigo y version.') from exc

    def update(self, template_id: str, payload: dict):
        payload = _normalize_template_payload(payload)
        template = self.get_by_id(template_id)
        for key, value in payload.items():
            setattr(template, key, value)
        try:
            template.save()
            return template
        except NotUniqueError as exc:
            raise ConflictError('La actualizacion genera conflicto por codigo/version.') from exc

    def delete(self, template_id: str):
        template = self.get_by_id(template_id)
        template.delete()
