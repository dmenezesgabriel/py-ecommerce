import json
import logging

import pika
from src.infrastructure.messaging.base import BaseMessagingAdapter

logger = logging.getLogger("app")


class PaymentPublisher(BaseMessagingAdapter):
    def __init__(self, connection_params, max_retries=5, delay=5):
        super().__init__(connection_params, max_retries, delay)
        self.exchange_name = "payment_exchange"

    def publish_payment_update(
        self, payment_id: str, order_id: int, status: str
    ):
        message = json.dumps(
            {
                "payment_id": payment_id,
                "order_id": order_id,
                "status": status,
            }
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="payment_queue",
                body=message,
            )
            logger.info(
                f"Published payment update: {message} to payment_queue"
            )
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_payment_update(payment_id, order_id, status)
