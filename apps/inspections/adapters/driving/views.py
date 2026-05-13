"""
Driving Adapters — Views DRF para el bounded context Inspections.

Responsabilidad: traducir HTTP → Use Case → HTTP.
"""

from rest_framework.views import APIView

from apps.common.presentation.api_response import success_response
from apps.inspections.adapters.driving.serializers import (
    DateRangeQuerySerializer,
    InspectionCloseSerializer,
    InspectionCreateSerializer,
    InspectionFilterSerializer,
    InspectionOutputSerializer,
    InspectionPaginatedOutputSerializer,
    InspectionStatusTransitionSerializer,
    InspectionUpdateSerializer,
)
from apps.inspections.application.factory import get_inspection_use_cases


class InspectionCollectionView(APIView):
    def get(self, request):
        use_cases = get_inspection_use_cases()
        entities = use_cases.list_inspections()
        serializer = InspectionOutputSerializer(entities, many=True)
        return success_response(serializer.data)

    def post(self, request):
        use_cases = get_inspection_use_cases()
        serializer = InspectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.create_inspection(serializer.validated_data)
        out = InspectionOutputSerializer(entity)
        return success_response(
            out.data, message='Inspeccion creada en borrador.', status=201
        )


class InspectionDetailView(APIView):
    def get(self, request, inspection_id):
        use_cases = get_inspection_use_cases()
        entity = use_cases.get_inspection(inspection_id)
        serializer = InspectionOutputSerializer(entity)
        return success_response(serializer.data)

    def put(self, request, inspection_id):
        use_cases = get_inspection_use_cases()
        serializer = InspectionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.update_inspection(
            inspection_id, serializer.validated_data
        )
        out = InspectionOutputSerializer(entity)
        return success_response(out.data, message='Inspeccion actualizada.')

    def delete(self, request, inspection_id):
        use_cases = get_inspection_use_cases()
        data = use_cases.delete_inspection(inspection_id)
        return success_response(data, message='Inspeccion eliminada.')


class InspectionByPlateView(APIView):
    def get(self, request, plate):
        use_cases = get_inspection_use_cases()
        entities = use_cases.find_by_plate(plate)
        serializer = InspectionOutputSerializer(entities, many=True)
        return success_response(serializer.data)


class InspectionByDateView(APIView):
    def get(self, request):
        use_cases = get_inspection_use_cases()
        serializer = DateRangeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        entities = use_cases.find_by_date_range(
            serializer.validated_data['start'],
            serializer.validated_data['end'],
        )
        out = InspectionOutputSerializer(entities, many=True)
        return success_response(out.data)


class InspectionByStatusView(APIView):
    def get(self, request, status):
        use_cases = get_inspection_use_cases()
        entities = use_cases.find_by_status(status)
        serializer = InspectionOutputSerializer(entities, many=True)
        return success_response(serializer.data)


class InspectionByVehicleView(APIView):
    def get(self, request, vehicle_id):
        use_cases = get_inspection_use_cases()
        entities = use_cases.find_by_vehicle_id(int(vehicle_id))
        serializer = InspectionOutputSerializer(entities, many=True)
        return success_response(serializer.data)


class InspectionSaveDraftView(APIView):
    def patch(self, request, inspection_id):
        use_cases = get_inspection_use_cases()
        serializer = InspectionStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.save_draft(
            inspection_id, serializer.validated_data
        )
        out = InspectionOutputSerializer(entity)
        return success_response(
            out.data, message='Inspeccion guardada en borrador.'
        )


class InspectionInProgressView(APIView):
    def patch(self, request, inspection_id):
        use_cases = get_inspection_use_cases()
        serializer = InspectionStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.mark_in_progress(
            inspection_id, serializer.validated_data
        )
        out = InspectionOutputSerializer(entity)
        return success_response(
            out.data, message='Inspeccion marcada en progreso.'
        )


class InspectionCloseView(APIView):
    def patch(self, request, inspection_id):
        use_cases = get_inspection_use_cases()
        serializer = InspectionCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.close_inspection(
            inspection_id, serializer.validated_data
        )
        out = InspectionOutputSerializer(entity)
        return success_response(out.data, message='Inspeccion cerrada.')


class InspectionSearchView(APIView):
    def get(self, request):
        serializer = InspectionFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        page = validated.get('page', 1)
        page_size = validated.get('page_size', 20)

        use_cases = get_inspection_use_cases()
        items, total_count = use_cases.list_inspections_paginated(
            page=page,
            page_size=page_size,
            plate=validated.get('plate'),
            status=validated.get('status'),
            vehicle_id=validated.get('vehicle_id'),
            start_date=validated.get('start_date'),
            end_date=validated.get('end_date'),
        )

        total_pages = (total_count + page_size - 1) // page_size

        output_serializer = InspectionOutputSerializer(items, many=True)
        pagination_info = {
            'page': page,
            'page_size': page_size,
            'total_items': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        }

        response_data = {
            'items': output_serializer.data,
            'pagination': pagination_info,
        }
        return success_response(response_data)
