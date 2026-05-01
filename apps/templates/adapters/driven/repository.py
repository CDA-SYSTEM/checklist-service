"""
Driven Adapter — Implementación MongoDB del TemplateRepositoryPort.
"""

from mongoengine.errors import NotUniqueError

from apps.common.domain.exceptions import ConflictError, NotFoundError, ValidationError
from apps.templates.adapters.driven.documents import (
    ChecklistTemplate,
    TemplateItem,
    TemplateSection,
    TemplateSubsection,
)
from apps.templates.adapters.driven.mappers import TemplateMapper
from apps.templates.domain.entities import TemplateEntity
from apps.templates.domain.ports import TemplateRepositoryPort


def _build_template_items(items_payload: list | None) -> list[TemplateItem]:
    if not items_payload:
        return []
    if not isinstance(items_payload, list):
        raise ValidationError('El campo items de una subseccion debe ser una lista.')

    built = []
    for item in items_payload:
        if isinstance(item, TemplateItem):
            built.append(item)
        elif isinstance(item, dict):
            built.append(
                TemplateItem(
                    code=item.get('code'),
                    description=item.get('description'),
                    defect_type=item.get('defect_type'),
                    observation=item.get('observation', ''),
                    order=item.get('order'),
                )
            )
        else:
            raise ValidationError('Cada item de subseccion debe ser un objeto valido.')
    return built


def _build_template_subsections(
    subsections_payload: list | None,
) -> list[TemplateSubsection]:
    if not subsections_payload:
        return []
    if not isinstance(subsections_payload, list):
        raise ValidationError(
            'El campo subsections de una seccion debe ser una lista.'
        )

    built = []
    for sub in subsections_payload:
        if isinstance(sub, TemplateSubsection):
            built.append(sub)
        elif isinstance(sub, dict):
            built.append(
                TemplateSubsection(
                    code=sub.get('code'),
                    title=sub.get('title'),
                    order=sub.get('order'),
                    items=_build_template_items(sub.get('items', [])),
                )
            )
        else:
            raise ValidationError('Cada subseccion debe ser un objeto valido.')
    return built


def _build_template_sections(
    sections_payload: list | None,
) -> list[TemplateSection]:
    if not sections_payload:
        return []
    if not isinstance(sections_payload, list):
        raise ValidationError('El campo sections debe ser una lista.')

    built = []
    for sec in sections_payload:
        if isinstance(sec, TemplateSection):
            built.append(sec)
        elif isinstance(sec, dict):
            built.append(
                TemplateSection(
                    code=sec.get('code'),
                    title=sec.get('title'),
                    order=sec.get('order'),
                    subsections=_build_template_subsections(
                        sec.get('subsections', [])
                    ),
                )
            )
        else:
            raise ValidationError('Cada seccion debe ser un objeto valido.')
    return built


def _normalize_payload(payload: dict) -> dict:
    """Normaliza el payload convirtiendo secciones dict a EmbeddedDocuments."""
    normalized = dict(payload)
    if 'sections' in normalized:
        normalized['sections'] = _build_template_sections(normalized['sections'])
    return normalized


class MongoTemplateRepository(TemplateRepositoryPort):
    """Driven adapter — implementa TemplateRepositoryPort con MongoDB."""

    def list_all(self) -> list[TemplateEntity]:
        docs = ChecklistTemplate.objects.order_by('-updated_at')
        return [TemplateMapper.to_entity(d) for d in docs]

    def list_by_vehicle_type(
        self, vehicle_type: str, *, active_only: bool = False
    ) -> list[TemplateEntity]:
        query = ChecklistTemplate.objects.filter(
            supported_vehicle_types=vehicle_type
        )
        if active_only:
            query = query.filter(active=True)
        return [TemplateMapper.to_entity(d) for d in query.order_by('-version')]

    def get_by_id(self, template_id: str) -> TemplateEntity:
        doc = ChecklistTemplate.objects(id=template_id).first()
        if not doc:
            raise NotFoundError('Plantilla no encontrada.')
        return TemplateMapper.to_entity(doc)

    def get_by_code_and_version(
        self, code: str, version: int
    ) -> TemplateEntity | None:
        doc = ChecklistTemplate.objects(code=code, version=version).first()
        return TemplateMapper.to_entity(doc) if doc else None

    def get_active_by_vehicle_type(self, vehicle_type: str) -> TemplateEntity:
        doc = (
            ChecklistTemplate.objects(
                supported_vehicle_types=vehicle_type, active=True
            )
            .order_by('-version')
            .first()
        )
        if not doc:
            raise NotFoundError(
                'No existe plantilla activa para el tipo de vehiculo solicitado.'
            )
        return TemplateMapper.to_entity(doc)

    def get_latest_version(self, code: str) -> TemplateEntity | None:
        doc = ChecklistTemplate.objects(code=code).order_by('-version').first()
        return TemplateMapper.to_entity(doc) if doc else None

    def deactivate_versions(self, code: str) -> None:
        ChecklistTemplate.objects(code=code, active=True).update(active=False)

    def create(self, entity: TemplateEntity) -> TemplateEntity:
        fields = TemplateMapper.to_document_fields(entity)
        fields['version'] = entity.version
        try:
            doc = ChecklistTemplate(**fields)
            doc.save()
            return TemplateMapper.to_entity(doc)
        except NotUniqueError as exc:
            raise ConflictError(
                'Ya existe una plantilla con el mismo codigo y version.'
            ) from exc

    def update(self, template_id: str, entity: TemplateEntity) -> TemplateEntity:
        doc = ChecklistTemplate.objects(id=template_id).first()
        if not doc:
            raise NotFoundError('Plantilla no encontrada.')

        fields = TemplateMapper.to_document_fields(entity)
        for key, value in fields.items():
            setattr(doc, key, value)
        try:
            doc.save()
            return TemplateMapper.to_entity(doc)
        except NotUniqueError as exc:
            raise ConflictError(
                'La actualizacion genera conflicto por codigo/version.'
            ) from exc

    def delete(self, template_id: str) -> None:
        doc = ChecklistTemplate.objects(id=template_id).first()
        if not doc:
            raise NotFoundError('Plantilla no encontrada.')
        doc.delete()
