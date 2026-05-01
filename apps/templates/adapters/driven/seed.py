"""
Bootstrap automático de plantillas desde archivos JSON.
"""

import json
import logging
from pathlib import Path

from apps.templates.adapters.driven.documents import ChecklistTemplate
from apps.templates.adapters.driven.repository import MongoTemplateRepository

logger = logging.getLogger(__name__)


def _seed_files() -> list[Path]:
    seed_dir = Path(__file__).resolve().parent / 'seed_data'
    return [
        seed_dir / 'motos.json',
        seed_dir / 'livianos_pesados.json',
    ]


def _read_seed_payload(seed_file: Path) -> dict | None:
    if not seed_file.exists():
        logger.warning('No se encontro archivo de seed: %s', seed_file)
        return None

    with seed_file.open('r', encoding='utf-8') as source:
        payload = json.load(source)

    required_fields = {'code', 'name', 'version', 'active', 'supported_vehicle_types', 'sections'}
    missing = required_fields - set(payload.keys())
    if missing:
        logger.warning(
            'El archivo %s no tiene los campos requeridos: %s',
            seed_file,
            sorted(missing),
        )
        return None

    return payload


def bootstrap_templates():
    """Carga las plantillas iniciales desde JSON si no existen."""
    ChecklistTemplate.ensure_indexes()
    repository = MongoTemplateRepository()

    for seed_file in _seed_files():
        payload = _read_seed_payload(seed_file)
        if payload is None:
            continue

        existing = repository.get_by_code_and_version(
            payload['code'], payload['version']
        )
        if existing:
            continue

        if payload.get('active', True):
            repository.deactivate_versions(payload['code'])

        from apps.templates.adapters.driven.documents import (
            ChecklistTemplate as CT,
        )
        from apps.templates.adapters.driven.repository import _normalize_payload

        normalized = _normalize_payload(payload)
        doc = CT(**normalized)
        doc.save()
        logger.info('Seed cargado: %s v%s', payload['code'], payload['version'])
