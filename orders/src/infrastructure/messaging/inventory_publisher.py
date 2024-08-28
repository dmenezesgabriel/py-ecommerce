import json
import logging

import pika
from src.infrastructure.messaging.base import BaseMessagingAdapter

logger = logging.getLogger("app")


class InventoryPublisher(BaseMessagingAdapter):
    def __init__(self, connection_params, max_retries=5, delay=5):
        super().__init__(connection_params, max_retries, delay)
        self.exchange_name = "inventory_exchange"

    def publish_inventory_update(self, sku: str, action: str, quantity: int):
        message = json.dumps(
            {"sku": sku, "action": action, "quantity": quantity}
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="inventory_queue",
                body=message,
            )
            logger.info(f"Published inventory update: {message}")
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_inventory_update(sku, action, quantity)
