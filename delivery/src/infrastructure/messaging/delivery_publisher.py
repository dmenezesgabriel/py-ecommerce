import json
import logging
import socket
import time

import pika

logger = logging.getLogger()


class DeliveryPublisher:
    def __init__(self, connection_params, max_retries=5, delay=5):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None
        self.channel = None
        self.exchange_name = "delivery_exchange"
        self.connect()

    def connect(self):
        attempts = 0
        while attempts < self.max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    self.connection_params
                )
                self.channel = self.connection.channel()
                return
            except (pika.exceptions.AMQPConnectionError, socket.gaierror) as e:
                attempts += 1
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        raise pika.exceptions.AMQPConnectionError(
            "Failed to connect to RabbitMQ after multiple attempts."
        )

    def publish_delivery_update(
        self, delivery_id: int, order_id: int, status: str
    ):
        message = json.dumps(
            {
                "delivery_id": delivery_id,
                "order_id": order_id,
                "status": status,
            }
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="delivery_queue",
                body=message,
            )
            logger.info(
                f"Published delivery update: {message} to delivery_queue"
            )
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_delivery_update(delivery_id, order_id, status)
