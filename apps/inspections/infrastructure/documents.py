from datetime import UTC, datetime

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    IntField,
    ListField,
    StringField,
)

from apps.common.domain.constants import DefectType, GeneralResult, InspectionStatus, VehicleType


class TemplateReference(EmbeddedDocument):
    template_id = StringField(required=True)
    code = StringField(required=True)
    version = IntField(required=True)


class InspectionItemResponse(EmbeddedDocument):
    section_code = StringField(required=True)
    subsection_code = StringField(required=True)
    item_code = StringField(required=True)
    response = StringField(required=True)
    defect_type = StringField(choices=DefectType.ALL)
    observation = StringField(default='')


class TireMeasurement(EmbeddedDocument):
    tire_code = StringField(required=True)
    outer_mm = FloatField(required=True, min_value=0)
    middle_mm = FloatField(required=True, min_value=0)
    inner_mm = FloatField(required=True, min_value=0)
    minimum_mm = FloatField(required=True, min_value=0)


class WheelMeasurement(EmbeddedDocument):
    wheel_code = StringField(required=True)
    tires = ListField(EmbeddedDocumentField(TireMeasurement), default=list)
    minimum_mm = FloatField(required=True, min_value=0)


class AxleMeasurement(EmbeddedDocument):
    axle_code = StringField(required=True)
    wheels = ListField(EmbeddedDocumentField(WheelMeasurement), default=list)
    minimum_mm = FloatField(required=True, min_value=0)


class LabradoMeasurement(EmbeddedDocument):
    axles = ListField(EmbeddedDocumentField(AxleMeasurement), default=list)
    minimum_mm = FloatField(required=True, min_value=0)
    measured_at = DateTimeField(default=lambda: datetime.now(UTC))


class Inspection(Document):
    plate = StringField(required=True)
    vehicle_id = StringField(required=True)
    client_id = StringField()
    vehicle_type = StringField(required=True, choices=VehicleType.ALL)
    inspection_datetime = DateTimeField(default=lambda: datetime.now(UTC))
    operators = ListField(StringField(), default=list)
    status = StringField(required=True, choices=InspectionStatus.ALL, default=InspectionStatus.BORRADOR)
    responses = ListField(EmbeddedDocumentField(InspectionItemResponse), default=list)
    observations = StringField(default='')
    general_result = StringField(choices=GeneralResult.ALL)
    template_ref = EmbeddedDocumentField(TemplateReference, required=True)
    template_snapshot = DictField(default=dict)
    labrado = EmbeddedDocumentField(LabradoMeasurement)
    created_at = DateTimeField(default=lambda: datetime.now(UTC))
    updated_at = DateTimeField(default=lambda: datetime.now(UTC))

    meta = {
        'collection': 'inspections',
        'indexes': [
            'plate',
            'vehicle_id',
            'status',
            'inspection_datetime',
            {'fields': ['plate', '-inspection_datetime']},
            {'fields': ['vehicle_id', '-inspection_datetime']},
            {'fields': ['status', '-inspection_datetime']},
        ],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(UTC)
        return super().save(*args, **kwargs)
