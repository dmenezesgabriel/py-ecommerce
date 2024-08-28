import logging
import socket
import time

import pika

logger = logging.getLogger("app")


class BaseMessagingAdapter:
    def __init__(self, connection_params, max_retries=5, delay=5):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None
        self.channel = None
        self.exchange_name = None  # Set in derived classes
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
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                attempts += 1
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        raise pika.exceptions.AMQPConnectionError(
            "Failed to connect to RabbitMQ after multiple attempts."
        )
