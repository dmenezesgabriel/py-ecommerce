import json
import logging
import socket
import time

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic

from src.application.services.product_service import ProductService
from src.config import Config

logger = logging.getLogger()


class InventorySubscriber:
    def __init__(
        self,
        product_service: ProductService,
        max_retries: int = 5,
        delay: int = 5,
    ):
        self.product_service = product_service
        self.connection_params = pika.ConnectionParameters(
            host=Config.BROKER_HOST, heartbeat=120
        )
        self.max_retries = max_retries
        self.delay = delay

    def connect(self) -> bool:
        attempts = 0
        while attempts < self.max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    self.connection_params
                )
                self.channel = self.connection.channel()
                return True
            except (pika.exceptions.AMQPConnectionError, socket.gaierror) as e:
                attempts += 1
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        return False

    def start_consuming(self) -> None:
        if not self.connect():
            logger.error("Failed to start consuming. Exiting.")
            return

        self.channel.exchange_declare(
            exchange="inventory_exchange", exchange_type="direct", durable=True
        )
        self.channel.queue_declare(queue="inventory_queue", durable=True)
        self.channel.queue_bind(
            exchange="inventory_exchange",
            queue="inventory_queue",
            routing_key="inventory_queue",
        )

        self.channel.basic_consume(
            queue="inventory_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )

        logger.info("Starting to consume messages from inventory_queue.")
        self.channel.start_consuming()

    def on_message(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: Basic,
        body: bytes,
    ) -> None:
        logger.info(f"Received message from inventory_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            sku = data.get("sku")
            action = data.get("action")
            quantity = data.get("quantity")

            if action == "add":
                self.product_service.add_inventory(sku, quantity)
                logger.info(f"Added {quantity} to SKU: {sku}.")
            elif action == "subtract":
                self.product_service.subtract_inventory(sku, quantity)
                logger.info(f"Subtracted {quantity} from SKU: {sku}.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
