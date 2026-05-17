"""
Driven Adapter — RabbitMQ RPC client para validar existencia de vehículo y cliente.

Implementa EntityExistencePort usando el patrón RPC de RabbitMQ.
Compatible con el mismo formato que usan los microservicios NestJS
(clients-services y vehicles-services).
"""

from __future__ import annotations

import json
import logging
import uuid

from apps.common.domain.exceptions import ServiceUnavailableError, ValidationError
from apps.inspections.domain.ports import EntityExistencePort

logger = logging.getLogger(__name__)

_PATTERN_CLIENT_EXISTS = "cda.client.exists"
_PATTERN_VEHICLE_EXISTS = "cda.vehicle.exists"


class RabbitMQExistenceValidator(EntityExistencePort):
    """
    Valida existencia de cliente y vehículo vía RabbitMQ RPC.

    Si no se configura RABBITMQ_URI la validación se omite (modo dev).
    """

    def __init__(
        self,
        rabbitmq_url: str | None,
        client_queue: str = "client-service-queue",
        vehicle_queue: str = "vehicle-service-queue",
        timeout_ms: int = 8000,
    ):
        self._rabbitmq_url = rabbitmq_url
        self._client_queue = client_queue
        self._vehicle_queue = vehicle_queue
        self._timeout_s = timeout_ms / 1000

    def _parse_rpc_response(self, result: dict, entity_label: str, entity_id: int) -> None:
        if result.get("err"):
            raise ServiceUnavailableError(
                f"Error en validacion de {entity_label}: {result['err']}"
            )
        response_data = result.get("response") or {}
        if not response_data.get("exists"):
            raise ValidationError(
                f"{entity_label.capitalize()} no encontrado o invalido: {entity_id}"
            )

    def assert_vehicle_exists(self, vehicle_id: int) -> None:
        if not self._rabbitmq_url:
            logger.info("RabbitMQ desactivado — saltando validacion de vehiculo")
            return
        result = self._rpc_call(
            queue=self._vehicle_queue,
            pattern=_PATTERN_VEHICLE_EXISTS,
            payload={"id": str(vehicle_id)},
        )
        self._parse_rpc_response(result, "vehiculo", vehicle_id)

    def assert_client_exists(self, client_id: int) -> None:
        if not self._rabbitmq_url:
            logger.info("RabbitMQ desactivado — saltando validacion de cliente")
            return
        result = self._rpc_call(
            queue=self._client_queue,
            pattern=_PATTERN_CLIENT_EXISTS,
            payload={"id": str(client_id)},
        )
        self._parse_rpc_response(result, "cliente", client_id)

    def _rpc_call(self, queue: str, pattern: str, payload: dict) -> dict:
        import pika

        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(self._rabbitmq_url),
            )
            channel = connection.channel()

            corr_id = str(uuid.uuid4())
            callback = channel.queue_declare(queue="", exclusive=True)
            callback_queue = callback.method.queue

            response_holder: list[dict | None] = [None]

            def on_response(_ch, _method, props, body):
                if props.correlation_id == corr_id:
                    response_holder[0] = json.loads(body)

            channel.basic_consume(
                queue=callback_queue,
                on_message_callback=on_response,
                auto_ack=True,
            )

            message = json.dumps({"pattern": pattern, "data": payload, "id": corr_id})
            channel.basic_publish(
                exchange="",
                routing_key=queue,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    content_encoding="utf-8",
                    correlation_id=corr_id,
                    reply_to=callback_queue,
                    delivery_mode=2,
                ),
                body=message.encode("utf-8"),
            )

            deadline = self._timeout_s
            while deadline > 0 and response_holder[0] is None:
                try:
                    channel.connection.process_data_events(time_limit=1)
                except Exception:
                    break
                deadline -= 1

            connection.close()

            if response_holder[0] is None:
                raise TimeoutError(
                    f"RPC timeout tras {self._timeout_s}s para {pattern}"
                )

            return response_holder[0]

        except TimeoutError:
            raise ServiceUnavailableError(
                f"No se pudo validar con microservicios (RabbitMQ). "
                f"Timeout en {pattern} para {queue}."
            )
        except Exception as exc:
            logger.exception("Error en RPC call a %s: %s", queue, exc)
            raise ServiceUnavailableError(
                f"No se pudo validar con microservicios (RabbitMQ). Fallo: {exc}"
            )
