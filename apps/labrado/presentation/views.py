from rest_framework.views import APIView

from apps.common.presentation.api_response import success_response
from apps.labrado.application.use_cases import LabradoUseCases
from apps.labrado.presentation.serializers import (
    LabradoCreateSerializer,
    LabradoOutputSerializer,
    LabradoUpdateSerializer,
)


class LabradoCollectionView(APIView):
    use_cases = LabradoUseCases()

    def post(self, request):
        serializer = LabradoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.upsert_labrado(
            serializer.validated_data['inspection_id'], serializer.validated_data['axles']
        )
        out = LabradoOutputSerializer(data)
        return success_response(out.data, message='Labrado registrado.', status=201)


class LabradoByInspectionView(APIView):
    use_cases = LabradoUseCases()

    def get(self, request, inspection_id):
        data = self.use_cases.get_labrado_by_inspection(inspection_id)
        serializer = LabradoOutputSerializer(data)
        return success_response(serializer.data)

    def put(self, request, inspection_id):
        serializer = LabradoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.upsert_labrado(inspection_id, serializer.validated_data['axles'])
        out = LabradoOutputSerializer(data)
        return success_response(out.data, message='Labrado actualizado.')
