"""
Serializers DRF para el bounded context Labrado.

Driving adapters — traducen entre HTTP request/response y el dominio.
"""

from rest_framework import serializers


class TireMeasurementSerializer(serializers.Serializer):
    tire_code = serializers.CharField()
    outer_mm = serializers.FloatField(min_value=0)
    middle_mm = serializers.FloatField(min_value=0)
    inner_mm = serializers.FloatField(min_value=0)


class WheelMeasurementSerializer(serializers.Serializer):
    wheel_code = serializers.CharField()
    tires = TireMeasurementSerializer(many=True)


class AxleMeasurementSerializer(serializers.Serializer):
    axle_code = serializers.CharField()
    wheels = WheelMeasurementSerializer(many=True)


class LabradoCreateSerializer(serializers.Serializer):
    inspection_id = serializers.CharField()
    axles = AxleMeasurementSerializer(many=True)


class LabradoUpdateSerializer(serializers.Serializer):
    axles = AxleMeasurementSerializer(many=True)


class LabradoOutputSerializer(serializers.Serializer):
    inspection_id = serializers.CharField()
    labrado = serializers.JSONField(allow_null=True)
