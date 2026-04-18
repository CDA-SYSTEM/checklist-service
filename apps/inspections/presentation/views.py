from rest_framework.views import APIView

from apps.common.presentation.api_response import success_response
from apps.inspections.application.use_cases import InspectionUseCases
from apps.inspections.presentation.serializers import (
    DateRangeQuerySerializer,
    InspectionCloseSerializer,
    InspectionCreateSerializer,
    InspectionOutputSerializer,
    InspectionStatusTransitionSerializer,
    InspectionUpdateSerializer,
)


class InspectionCollectionView(APIView):
    use_cases = InspectionUseCases()

    def get(self, request):
        data = self.use_cases.list_inspections()
        serializer = InspectionOutputSerializer(data, many=True)
        return success_response(serializer.data)

    def post(self, request):
        serializer = InspectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.create_inspection(serializer.validated_data)
        out = InspectionOutputSerializer(data)
        return success_response(out.data, message='Inspeccion creada en borrador.', status=201)


class InspectionDetailView(APIView):
    use_cases = InspectionUseCases()

    def get(self, request, inspection_id):
        data = self.use_cases.get_inspection(inspection_id)
        serializer = InspectionOutputSerializer(data)
        return success_response(serializer.data)

    def put(self, request, inspection_id):
        serializer = InspectionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.update_inspection(inspection_id, serializer.validated_data)
        out = InspectionOutputSerializer(data)
        return success_response(out.data, message='Inspeccion actualizada.')

    def delete(self, request, inspection_id):
        data = self.use_cases.delete_inspection(inspection_id)
        return success_response(data, message='Inspeccion eliminada.')


class InspectionByPlateView(APIView):
    use_cases = InspectionUseCases()

    def get(self, request, plate):
        data = self.use_cases.find_by_plate(plate)
        serializer = InspectionOutputSerializer(data, many=True)
        return success_response(serializer.data)


class InspectionByDateView(APIView):
    use_cases = InspectionUseCases()

    def get(self, request):
        serializer = DateRangeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.find_by_date_range(
            serializer.validated_data['start'], serializer.validated_data['end']
        )
        out = InspectionOutputSerializer(data, many=True)
        return success_response(out.data)


class InspectionByStatusView(APIView):
    use_cases = InspectionUseCases()

    def get(self, request, status):
        data = self.use_cases.find_by_status(status)
        serializer = InspectionOutputSerializer(data, many=True)
        return success_response(serializer.data)


class InspectionByVehicleView(APIView):
    use_cases = InspectionUseCases()

    def get(self, request, vehicle_id):
        data = self.use_cases.find_by_vehicle_id(vehicle_id)
        serializer = InspectionOutputSerializer(data, many=True)
        return success_response(serializer.data)


class InspectionSaveDraftView(APIView):
    use_cases = InspectionUseCases()

    def patch(self, request, inspection_id):
        serializer = InspectionStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.save_draft(inspection_id, serializer.validated_data)
        out = InspectionOutputSerializer(data)
        return success_response(out.data, message='Inspeccion guardada en borrador.')


class InspectionInProgressView(APIView):
    use_cases = InspectionUseCases()

    def patch(self, request, inspection_id):
        serializer = InspectionStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.mark_in_progress(inspection_id, serializer.validated_data)
        out = InspectionOutputSerializer(data)
        return success_response(out.data, message='Inspeccion marcada en progreso.')


class InspectionCloseView(APIView):
    use_cases = InspectionUseCases()

    def patch(self, request, inspection_id):
        serializer = InspectionCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.close_inspection(inspection_id, serializer.validated_data)
        out = InspectionOutputSerializer(data)
        return success_response(out.data, message='Inspeccion cerrada.')
