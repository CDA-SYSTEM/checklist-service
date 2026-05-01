from django.apps import AppConfig


class InspectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inspections'

    _indexes_ready = False

    def ready(self):
        if InspectionsConfig._indexes_ready:
            return

        InspectionsConfig._indexes_ready = True
        from apps.inspections.adapters.driven.documents import Inspection

        Inspection.ensure_indexes()
