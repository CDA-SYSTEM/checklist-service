from django.urls import path

from apps.labrado.presentation.views import LabradoByInspectionView, LabradoCollectionView

urlpatterns = [
    path('labrado', LabradoCollectionView.as_view(), name='labrado-collection'),
    path(
        'labrado/by-inspection/<str:inspection_id>',
        LabradoByInspectionView.as_view(),
        name='labrado-by-inspection',
    ),
]
