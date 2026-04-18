from rest_framework.views import APIView

from apps.common.presentation.api_response import success_response
from apps.templates.application.use_cases import TemplateUseCases
from apps.templates.presentation.serializers import TemplateCreateUpdateSerializer, TemplateOutputSerializer


class TemplateCollectionView(APIView):
    use_cases = TemplateUseCases()

    def get(self, request):
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            data = self.use_cases.list_templates_by_vehicle_type(vehicle_type)
        else:
            data = self.use_cases.list_templates()
        serializer = TemplateOutputSerializer(data, many=True)
        return success_response(serializer.data)

    def post(self, request):
        serializer = TemplateCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.create_template(serializer.validated_data)
        out = TemplateOutputSerializer(data)
        return success_response(out.data, message='Plantilla creada.', status=201)


class TemplateDetailView(APIView):
    use_cases = TemplateUseCases()

    def get(self, request, template_id):
        data = self.use_cases.get_template(template_id)
        serializer = TemplateOutputSerializer(data)
        return success_response(serializer.data)

    def put(self, request, template_id):
        serializer = TemplateCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.use_cases.update_template(template_id, serializer.validated_data)
        out = TemplateOutputSerializer(data)
        return success_response(out.data, message='Plantilla actualizada.')

    def delete(self, request, template_id):
        data = self.use_cases.delete_template(template_id)
        return success_response(data, message='Plantilla eliminada.')


class TemplateByVehicleTypeView(APIView):
    use_cases = TemplateUseCases()

    def get(self, request, vehicle_type):
        data = self.use_cases.get_active_template_by_vehicle_type(vehicle_type)
        serializer = TemplateOutputSerializer(data)
        return success_response(serializer.data)


class TemplateMotosView(APIView):
    use_cases = TemplateUseCases()

    def get(self, request):
        data = self.use_cases.get_motos_template()
        serializer = TemplateOutputSerializer(data)
        return success_response(serializer.data)


class TemplateLivianosPesadosView(APIView):
    use_cases = TemplateUseCases()

    def get(self, request):
        data = self.use_cases.get_livianos_pesados_template()
        serializer = TemplateOutputSerializer(data)
        return success_response(serializer.data)
