"""
Serializers DRF para el bounded context Templates.

Driving adapters — traducen entre HTTP request/response y el dominio.
"""

from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.common.domain.constants import DefectType, TemplateCode, VehicleType


class TemplateItemSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)
    description = serializers.CharField()
    defect_type = serializers.ChoiceField(choices=DefectType.ALL)
    observation = serializers.CharField(required=False, allow_blank=True, default='')
    order = serializers.IntegerField(min_value=1)


class TemplateSubsectionSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100, required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(min_value=1)
    items = TemplateItemSerializer(many=True, required=False, default=list)


class TemplateSectionSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100, required=False, allow_blank=True)
    title = serializers.CharField()
    order = serializers.IntegerField(min_value=1)
    subsections = TemplateSubsectionSerializer(many=True, required=False, default=list)


class TemplateCreateUpdateSerializer(serializers.Serializer):
    code = serializers.ChoiceField(
        choices=[TemplateCode.MOTOS, TemplateCode.LIVIANOS_PESADOS]
    )
    name = serializers.CharField(
        validators=[
            RegexValidator(
                regex='^(?![0-9]*$)[a-zA-Z0-9\\s]+$',
                message='El nombre debe contener letras y no puede ser solo numérico.',
            )
        ]
    )
    version = serializers.IntegerField(min_value=1, required=False)
    active = serializers.BooleanField(required=False, default=True)
    supported_vehicle_types = serializers.ListField(
        child=serializers.ChoiceField(choices=VehicleType.ALL),
        allow_empty=False,
    )
    sections = TemplateSectionSerializer(many=True, required=False, default=list)

    def validate_supported_vehicle_types(self, value):
        return sorted(set(value))


class TemplateOutputSerializer(serializers.Serializer):
    id = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()
    version = serializers.IntegerField()
    active = serializers.BooleanField()
    supported_vehicle_types = serializers.ListField(child=serializers.CharField())
    sections = TemplateSectionSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
