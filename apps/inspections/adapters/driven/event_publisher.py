"""
Driven Adapter - RabbitMQ publisher for inspection events.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from apps.common.domain.exceptions import ServiceUnavailableError
from apps.inspections.domain.entities import InspectionEntity
from apps.inspections.domain.ports import InspectionEventPublisherPort

logger = logging.getLogger(__name__)

ROUTING_KEY_INSPECCION_COMPLETADA = "inspeccion.planilla.completada"


class RabbitMQInspectionEventPublisher(InspectionEventPublisherPort):
    """Publishes inspection domain events to RabbitMQ."""

    def __init__(
        self,
        rabbitmq_url: str | None,
        exchange: str | None,
        queue: str | None = None,
    ):
        self._rabbitmq_url = rabbitmq_url
        self._exchange = exchange
        self._queue = queue

    def publish_inspection_completed(self, inspection: InspectionEntity) -> None:
        if not self._rabbitmq_url or not self._exchange:
            logger.info(
                "RabbitMQ publisher disabled - skipping inspection completed event"
            )
            return

        import pika

        connection = None
        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(self._rabbitmq_url),
            )
            channel = connection.channel()

            channel.exchange_declare(
                exchange=self._exchange,
                exchange_type="topic",
                durable=True,
            )

            if self._queue:
                channel.queue_declare(queue=self._queue, durable=True)
                channel.queue_bind(
                    queue=self._queue,
                    exchange=self._exchange,
                    routing_key=ROUTING_KEY_INSPECCION_COMPLETADA,
            )

            body = json.dumps(
                self._to_json_payload(inspection),
                ensure_ascii=False,
            ).encode("utf-8")

            channel.basic_publish(
                exchange=self._exchange,
                routing_key=ROUTING_KEY_INSPECCION_COMPLETADA,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    content_encoding="utf-8",
                    delivery_mode=2,
                    type=ROUTING_KEY_INSPECCION_COMPLETADA,
                ),
                body=body,
            )
        except Exception as exc:
            logger.exception(
                "Error publishing event %s: %s",
                ROUTING_KEY_INSPECCION_COMPLETADA,
                exc,
            )
            raise ServiceUnavailableError(
                "Could not publish the inspection completed event to RabbitMQ."
            )
        finally:
            if connection and not connection.is_closed:
                try:
                    connection.close()
                except Exception:
                    logger.warning("Could not close RabbitMQ connection cleanly")

    def _to_json_payload(self, inspection: InspectionEntity) -> dict[str, Any]:
        return self._to_json_compatible(inspection)

    def _to_json_compatible(self, value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, Enum):
            return value.value
        if is_dataclass(value):
            return {
                field.name: self._to_json_compatible(getattr(value, field.name))
                for field in fields(value)
            }
        if isinstance(value, Mapping):
            return {
                key: self._to_json_compatible(item)
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [self._to_json_compatible(item) for item in value]
        return value
