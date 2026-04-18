import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class TemplatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.templates'
    _seed_executed = False

    def ready(self):
        from apps.templates.infrastructure.documents import ChecklistTemplate

        ChecklistTemplate.ensure_indexes()

        if not settings.AUTO_SEED_TEMPLATES or TemplatesConfig._seed_executed:
            return

        TemplatesConfig._seed_executed = True
        try:
            from apps.templates.infrastructure.seed import bootstrap_templates

            bootstrap_templates()
        except Exception as exc:
            logger.warning('No fue posible ejecutar el seed de plantillas al iniciar: %s', exc)
