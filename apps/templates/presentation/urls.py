from django.urls import path

from apps.templates.presentation.views import (
    TemplateByVehicleTypeView,
    TemplateCollectionView,
    TemplateDetailView,
    TemplateLivianosPesadosView,
    TemplateMotosView,
)

urlpatterns = [
    path('templates', TemplateCollectionView.as_view(), name='templates-collection'),
    path('templates/motos', TemplateMotosView.as_view(), name='templates-motos'),
    path(
        'templates/livianos-pesados',
        TemplateLivianosPesadosView.as_view(),
        name='templates-livianos-pesados',
    ),
    path(
        'templates/active/<str:vehicle_type>',
        TemplateByVehicleTypeView.as_view(),
        name='templates-active-by-vehicle-type',
    ),
    path('templates/<str:template_id>', TemplateDetailView.as_view(), name='templates-detail'),
]
