import logging
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
            except pika.exceptions.AMQPConnectionError as e:
                attempts += 1
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} "
                    f"to connect to RabbitMQ failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        raise pika.exceptions.AMQPConnectionError(
            "Failed to connect to RabbitMQ after multiple attempts."
        )
