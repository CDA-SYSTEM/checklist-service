"""
Serializers DRF para el bounded context Inspections.

Driving adapters — traducen entre HTTP request/response y el dominio.
"""

from rest_framework import serializers

from apps.common.domain.constants import GeneralResult, InspectionStatus, VehicleType


class InspectionItemResponseSerializer(serializers.Serializer):
    section_code = serializers.CharField()
    subsection_code = serializers.CharField()
    item_code = serializers.CharField()
    response = serializers.CharField()
    defect_type = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    observation = serializers.CharField(
        required=False, allow_blank=True, default=''
    )


class TemplateReferenceSerializer(serializers.Serializer):
    template_id = serializers.CharField()
    code = serializers.CharField()
    version = serializers.IntegerField()


class InspectionCreateSerializer(serializers.Serializer):
    plate = serializers.CharField()
    vehicle_id = serializers.IntegerField()
    client_id = serializers.IntegerField(required=False, allow_null=True)
    vehicle_type = serializers.ChoiceField(choices=VehicleType.ALL)
    template_id = serializers.CharField(required=False, allow_blank=True)
    inspection_datetime = serializers.DateTimeField(required=False)
    inspector_id = serializers.CharField()
    responses = InspectionItemResponseSerializer(
        many=True, required=False, default=list
    )
    observations = serializers.CharField(
        required=False, allow_blank=True, default=''
    )


class InspectionUpdateSerializer(serializers.Serializer):
    plate = serializers.CharField(required=False)
    vehicle_id = serializers.IntegerField(required=False)
    client_id = serializers.IntegerField(required=False, allow_null=True)
    inspection_datetime = serializers.DateTimeField(required=False)
    inspector_id = serializers.CharField(required=False)
    responses = InspectionItemResponseSerializer(many=True, required=False)
    observations = serializers.CharField(required=False, allow_blank=True)


class InspectionCloseSerializer(InspectionUpdateSerializer):
    general_result = serializers.ChoiceField(choices=GeneralResult.ALL)


class InspectionStatusTransitionSerializer(InspectionUpdateSerializer):
    pass


class InspectionOutputSerializer(serializers.Serializer):
    id = serializers.CharField()
    plate = serializers.CharField()
    vehicle_id = serializers.IntegerField()
    client_id = serializers.IntegerField(allow_null=True, required=False)
    vehicle_type = serializers.ChoiceField(choices=VehicleType.ALL)
    inspection_datetime = serializers.DateTimeField()
    inspector_id = serializers.CharField()
    status = serializers.ChoiceField(choices=InspectionStatus.ALL)
    responses = InspectionItemResponseSerializer(many=True)
    observations = serializers.CharField(allow_blank=True)
    general_result = serializers.CharField(
        allow_blank=True, allow_null=True, required=False
    )
    template_ref = TemplateReferenceSerializer()
    template_snapshot = serializers.JSONField()
    labrado = serializers.JSONField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class DateRangeQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
