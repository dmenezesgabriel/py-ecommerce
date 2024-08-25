import json
import logging

from src.domain.entities.order_entity import OrderStatus
from src.infrastructure.messaging.base import BaseMessagingAdapter

logger = logging.getLogger("app")


class DeliverySubscriber(BaseMessagingAdapter):

    def __init__(
        self, order_service, connection_params, max_retries=5, delay=5
    ):
        super().__init__(connection_params, max_retries, delay)
        self.order_service = order_service

    def start_consuming(self):
        self.channel.exchange_declare(
            exchange="delivery_exchange", exchange_type="topic", durable=True
        )
        self.channel.queue_declare(queue="delivery_queue", durable=True)
        self.channel.queue_bind(
            exchange="delivery_exchange",
            queue="delivery_queue",
            routing_key="delivery_queue",
        )

        self.channel.basic_consume(
            queue="delivery_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )
        logger.info("Starting to consume messages from delivery_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from delivery_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            order_id = data.get("order_id")
            status = data.get("status")

            if status == "in_transit":
                self.order_service.update_order_status(
                    order_id, OrderStatus.SHIPPED
                )
                logger.info(f"Order ID {order_id} marked as shipped.")
            if status == "delivered":
                self.order_service.update_order_status(
                    order_id, OrderStatus.FINISHED
                )
                logger.info(f"Order ID {order_id} marked as finished.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
