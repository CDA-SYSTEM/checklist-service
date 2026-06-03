"""
URL routing para el bounded context Inspections.
"""

from django.urls import path

from apps.inspections.adapters.driving.views import (
    InspectionByDateView,
    InspectionByPlateView,
    InspectionByStatusView,
    InspectionByVehicleView,
    InspectionCloseView,
    InspectionCollectionView,
    InspectionDetailView,
    InspectionInProgressView,
    InspectionSaveDraftView,
    InspectionSearchView,
    InspectionStatsView,
)

urlpatterns = [
    path(
        'inspections',
        InspectionCollectionView.as_view(),
        name='inspections-collection',
    ),
    path(
        'inspections/by-plate/<str:plate>',
        InspectionByPlateView.as_view(),
        name='inspections-by-plate',
    ),
    path(
        'inspections/by-date',
        InspectionByDateView.as_view(),
        name='inspections-by-date',
    ),
    path(
        'inspections/by-status/<str:status>',
        InspectionByStatusView.as_view(),
        name='inspections-by-status',
    ),
    path(
        'inspections/by-vehicle/<str:vehicle_id>',
        InspectionByVehicleView.as_view(),
        name='inspections-by-vehicle',
    ),
    path(
        'inspections/search',
        InspectionSearchView.as_view(),
        name='inspections-search',
    ),
    path(
        'inspections/stats',
        InspectionStatsView.as_view(),
        name='inspection-stats',
    ),
    path(
        'inspections/<str:inspection_id>',
        InspectionDetailView.as_view(),
        name='inspections-detail',
    ),
    path(
        'inspections/<str:inspection_id>/draft',
        InspectionSaveDraftView.as_view(),
        name='inspections-save-draft',
    ),
    path(
        'inspections/<str:inspection_id>/in-progress',
        InspectionInProgressView.as_view(),
        name='inspections-in-progress',
    ),
    path(
        'inspections/<str:inspection_id>/close',
        InspectionCloseView.as_view(),
        name='inspections-close',
    ),
]
