from datetime import datetime, UTC

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    ListField,
    StringField,
)

from apps.common.domain.constants import DefectType, VehicleType


class TemplateItem(EmbeddedDocument):
    code = StringField(required=True)
    description = StringField(required=True)
    defect_type = StringField(required=True, choices=DefectType.ALL)
    observation = StringField(default='')
    order = IntField(required=True)
    source_row = IntField(required=True)


class TemplateSubsection(EmbeddedDocument):
    code = StringField(required=True)
    title = StringField(required=True)
    order = IntField(required=True)
    items = ListField(EmbeddedDocumentField(TemplateItem), default=list)


class TemplateSection(EmbeddedDocument):
    code = StringField(required=True)
    title = StringField(required=True)
    order = IntField(required=True)
    subsections = ListField(EmbeddedDocumentField(TemplateSubsection), default=list)


class ChecklistTemplate(Document):
    code = StringField(required=True)
    name = StringField(required=True)
    version = IntField(required=True, min_value=1)
    active = BooleanField(default=True)
    supported_vehicle_types = ListField(StringField(choices=VehicleType.ALL), required=True)
    sections = ListField(EmbeddedDocumentField(TemplateSection), default=list)
    source_file = StringField(default='')
    created_at = DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = DateTimeField(default=lambda: datetime.now(UTC))

    meta = {
        'collection': 'checklist_templates',
        'indexes': [
            {'fields': ['code', 'version'], 'unique': True},
            {'fields': ['code', 'active']},
            'supported_vehicle_types',
            {'fields': ['active', 'supported_vehicle_types']},
        ],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(UTC)
        return super().save(*args, **kwargs)
