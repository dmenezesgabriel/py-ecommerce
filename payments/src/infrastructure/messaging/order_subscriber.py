import json
import logging

import pika
from src.application.services.payment_service import PaymentService
from src.infrastructure.messaging.base import BaseMessagingAdapter

logger = logging.getLogger("app")


class OrderSubscriber(BaseMessagingAdapter):
    def __init__(
        self, payment_service: PaymentService, max_retries=5, delay=5
    ):
        self.payment_service = payment_service
        connection_params = pika.ConnectionParameters(
            host="rabbitmq", heartbeat=120
        )
        super().__init__(connection_params, max_retries, delay)

    def start_consuming(self):
        self.channel.exchange_declare(
            exchange="orders_exchange", exchange_type="topic", durable=True
        )
        self.channel.queue_declare(queue="orders_queue", durable=True)
        self.channel.queue_bind(
            exchange="orders_exchange",
            queue="orders_queue",
            routing_key="orders_queue",
        )

        self.channel.basic_consume(
            queue="orders_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )

        logger.info("Starting to consume messages from orders_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from orders_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            order_id = data.get("order_id")
            status = data.get("status")
            amount = data.get("amount")

            if status == "canceled":
                payment = self.payment_service.get_payment_by_order_id(
                    order_id
                )
                if payment.status in ["failed", "refunded", "canceled"]:
                    return
                self.payment_service.cancel_payment(payment.id)
                logger.info(f"Canceled payment for order ID: {order_id}.")

            if status == "confirmed":
                self.payment_service.create_payment(
                    order_id=order_id, amount=amount, status="pending"
                )
                logger.info(
                    f"Created pending payment for order ID: {order_id}."
                )
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
