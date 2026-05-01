"""
Mapper entre MongoEngine Documents y Domain Entities para Templates.
"""

from apps.templates.adapters.driven.documents import (
    ChecklistTemplate,
    TemplateItem,
    TemplateSection,
    TemplateSubsection,
)
from apps.templates.domain.entities import (
    TemplateEntity,
    TemplateItemEntity,
    TemplateSectionEntity,
    TemplateSubsectionEntity,
)


class TemplateMapper:
    """Convierte entre Document (persistencia) y Entity (dominio)."""

    @staticmethod
    def to_entity(doc: ChecklistTemplate) -> TemplateEntity:
        return TemplateEntity(
            id=str(doc.id),
            code=doc.code,
            name=doc.name,
            version=doc.version,
            active=doc.active,
            supported_vehicle_types=list(doc.supported_vehicle_types),
            sections=[
                TemplateSectionEntity(
                    code=s.code,
                    title=s.title,
                    order=s.order,
                    subsections=[
                        TemplateSubsectionEntity(
                            code=ss.code,
                            title=ss.title,
                            order=ss.order,
                            items=[
                                TemplateItemEntity(
                                    code=i.code,
                                    description=i.description,
                                    defect_type=i.defect_type,
                                    observation=i.observation,
                                    order=i.order,
                                )
                                for i in ss.items
                            ],
                        )
                        for ss in s.subsections
                    ],
                )
                for s in doc.sections
            ],
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    @staticmethod
    def to_document_fields(entity: TemplateEntity) -> dict:
        """Convierte entity a dict listo para crear/actualizar un Document."""
        fields = {
            'code': entity.code,
            'name': entity.name,
            'version': entity.version,
            'active': entity.active,
            'supported_vehicle_types': entity.supported_vehicle_types,
        }
        if entity.sections:
            fields['sections'] = [
                TemplateSection(
                    code=s.code,
                    title=s.title,
                    order=s.order,
                    subsections=[
                        TemplateSubsection(
                            code=ss.code,
                            title=ss.title,
                            order=ss.order,
                            items=[
                                TemplateItem(
                                    code=i.code,
                                    description=i.description,
                                    defect_type=i.defect_type,
                                    observation=i.observation,
                                    order=i.order,
                                )
                                for i in ss.items
                            ],
                        )
                        for ss in s.subsections
                    ],
                )
                for s in entity.sections
            ]
        return fields
