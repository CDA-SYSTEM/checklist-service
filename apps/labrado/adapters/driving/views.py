"""
Driving Adapters — Views DRF para el bounded context Labrado.

Responsabilidad: traducir HTTP → Use Case → HTTP.
"""

from rest_framework.views import APIView

from apps.common.presentation.api_response import success_response
from apps.labrado.adapters.driving.serializers import (
    LabradoCreateSerializer,
    LabradoOutputSerializer,
    LabradoUpdateSerializer,
)
from apps.labrado.application.factory import get_labrado_use_cases


class LabradoCollectionView(APIView):
    def post(self, request):
        use_cases = get_labrado_use_cases()
        serializer = LabradoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = use_cases.upsert_labrado(
            serializer.validated_data['inspection_id'],
            serializer.validated_data['axles'],
        )
        out = LabradoOutputSerializer(data)
        return success_response(
            out.data, message='Labrado registrado.', status=201
        )


class LabradoByInspectionView(APIView):
    def get(self, request, inspection_id):
        use_cases = get_labrado_use_cases()
        data = use_cases.get_labrado_by_inspection(inspection_id)
        serializer = LabradoOutputSerializer(data)
        return success_response(serializer.data)

    def put(self, request, inspection_id):
        use_cases = get_labrado_use_cases()
        serializer = LabradoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = use_cases.upsert_labrado(
            inspection_id, serializer.validated_data['axles']
        )
        out = LabradoOutputSerializer(data)
        return success_response(out.data, message='Labrado actualizado.')
