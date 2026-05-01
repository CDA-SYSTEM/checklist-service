"""
URL routing para el bounded context Labrado.
"""

from django.urls import path

from apps.labrado.adapters.driving.views import (
    LabradoByInspectionView,
    LabradoCollectionView,
)

urlpatterns = [
    path('labrado', LabradoCollectionView.as_view(), name='labrado-collection'),
    path(
        'labrado/by-inspection/<str:inspection_id>',
        LabradoByInspectionView.as_view(),
        name='labrado-by-inspection',
    ),
]
