"""
URL configuration for checklist-service.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.templates.adapters.driving.urls')),
    path('', include('apps.inspections.adapters.driving.urls')),
    path('', include('apps.labrado.adapters.driving.urls')),
]
