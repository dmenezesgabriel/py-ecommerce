import json
import logging

import pika
from src.infrastructure.messaging.base import BaseMessagingAdapter

logger = logging.getLogger("app")


class OrderUpdatePublisher(BaseMessagingAdapter):
    def __init__(self, connection_params, max_retries=5, delay=5):
        super().__init__(connection_params, max_retries, delay)
        self.exchange_name = "orders_exchange"

    def publish_order_update(self, order_id: int, amount: float, status: str):
        message = json.dumps(
            {"order_id": order_id, "amount": amount, "status": status}
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="orders_queue",
                body=message,
            )
            logging.info(f"Published order update: {message} to orders_queue")
        except pika.exceptions.ConnectionClosed:
            logging.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_order_update(order_id, amount, status)
