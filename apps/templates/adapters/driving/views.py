"""
Driving Adapters — Views DRF para el bounded context Templates.

Responsabilidad: traducir HTTP → Use Case → HTTP.
Usa factory para obtener use cases con dependencias inyectadas.
"""

from rest_framework.views import APIView

from apps.common.presentation.api_response import success_response
from apps.templates.adapters.driving.serializers import (
    TemplateCreateUpdateSerializer,
    TemplateOutputSerializer,
)
from apps.templates.application.factory import get_template_use_cases


class TemplateCollectionView(APIView):
    def get(self, request):
        use_cases = get_template_use_cases()
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            entities = use_cases.list_templates_by_vehicle_type(vehicle_type)
        else:
            entities = use_cases.list_templates()
        serializer = TemplateOutputSerializer(entities, many=True)
        return success_response(serializer.data)

    def post(self, request):
        use_cases = get_template_use_cases()
        serializer = TemplateCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.create_template(serializer.validated_data)
        out = TemplateOutputSerializer(entity)
        return success_response(out.data, message='Plantilla creada.', status=201)


class TemplateDetailView(APIView):
    def get(self, request, template_id):
        use_cases = get_template_use_cases()
        entity = use_cases.get_template(template_id)
        serializer = TemplateOutputSerializer(entity)
        return success_response(serializer.data)

    def put(self, request, template_id):
        use_cases = get_template_use_cases()
        serializer = TemplateCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entity = use_cases.update_template(template_id, serializer.validated_data)
        out = TemplateOutputSerializer(entity)
        return success_response(out.data, message='Plantilla actualizada.')

    def delete(self, request, template_id):
        use_cases = get_template_use_cases()
        data = use_cases.delete_template(template_id)
        return success_response(data, message='Plantilla eliminada.')


class TemplateByVehicleTypeView(APIView):
    def get(self, request, vehicle_type):
        use_cases = get_template_use_cases()
        entity = use_cases.get_active_template_by_vehicle_type(vehicle_type)
        serializer = TemplateOutputSerializer(entity)
        return success_response(serializer.data)


class TemplateMotosView(APIView):
    def get(self, request):
        use_cases = get_template_use_cases()
        entity = use_cases.get_motos_template()
        serializer = TemplateOutputSerializer(entity)
        return success_response(serializer.data)


class TemplateLivianosPesadosView(APIView):
    def get(self, request):
        use_cases = get_template_use_cases()
        entity = use_cases.get_livianos_pesados_template()
        serializer = TemplateOutputSerializer(entity)
        return success_response(serializer.data)
