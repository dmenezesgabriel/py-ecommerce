import json
import logging

from src.infrastructure.messaging.base import BaseMessagingAdapter

logger = logging.getLogger("app")


class PaymentSubscriber(BaseMessagingAdapter):
    def __init__(
        self, order_service, connection_params, max_retries=5, delay=5
    ):
        super().__init__(connection_params, max_retries, delay)
        self.order_service = order_service

    def start_consuming(self):
        self.channel.exchange_declare(
            exchange="payment_exchange", exchange_type="topic", durable=True
        )
        self.channel.queue_declare(queue="payment_queue", durable=True)
        self.channel.queue_bind(
            exchange="payment_exchange",
            queue="payment_queue",
            routing_key="payment_queue",
        )

        self.channel.basic_consume(
            queue="payment_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )
        logger.info("Starting to consume messages from payment_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from payment_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            order_id = data.get("order_id")
            status = data.get("status")

            if status == "completed":
                self.order_service.set_paid_order(order_id)
                logger.info(f"Order ID {order_id} marked as paid.")
            if status in ["refunded", "canceled"]:
                self.order_service.cancel_order(order_id)
                logger.info(f"Order ID {order_id} marked as canceled.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
