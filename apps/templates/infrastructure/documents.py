from mongoengine import Document, EmbeddedDocument, StringField, IntField, BooleanField, EmbeddedDocumentField, ListField

class ChecklistItem(EmbeddedDocument):
    code = StringField(required=True)
    description = StringField(required=True)
    defect_type = StringField(required=True, choices=["A", "B"])
    order = IntField(required=True)

class ChecklistSubsection(EmbeddedDocument):
    code = StringField(required=True)
    title = StringField(required=True)
    order = IntField(required=True)
    items = ListField(EmbeddedDocumentField(ChecklistItem))

class ChecklistSection(EmbeddedDocument):
    code = StringField(required=True)
    title = StringField(required=True)
    order = IntField(required=True)
    subsections = ListField(EmbeddedDocumentField(ChecklistSubsection))

class ChecklistTemplate(Document):
    code = StringField(required=True, unique=True)
    version = IntField(required=True)
    vehicle_type = StringField(required=True, choices=["MOTO", "LIVIANO", "PESADO"])
    active = BooleanField(default=True)
    sections = ListField(EmbeddedDocumentField(ChecklistSection))

    meta = {
        "collection": "checklist_templates",
        "indexes": [
            {"fields": ["code", "version"], "unique": True},
            "vehicle_type",
            "active"
        ]
    }