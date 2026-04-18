import json
import logging
from pathlib import Path

from apps.templates.infrastructure.documents import ChecklistTemplate
from apps.templates.infrastructure.repository import TemplateRepository

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
        logger.warning('El archivo %s no tiene los campos requeridos: %s', seed_file, sorted(missing))
        return None

    payload.setdefault('source_file', seed_file.name)
    return payload


def bootstrap_templates():
    ChecklistTemplate.ensure_indexes()
    repository = TemplateRepository()

    for seed_file in _seed_files():
        payload = _read_seed_payload(seed_file)
        if payload is None:
            continue

        exists = repository.get_by_code_and_version(payload['code'], payload['version'])
        if exists:
            continue

        if payload['active']:
            repository.deactivate_versions(payload['code'])

        repository.create(payload)
