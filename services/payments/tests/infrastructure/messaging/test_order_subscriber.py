import json
from unittest.mock import MagicMock, patch

import pytest
from src.domain.entities.payment_entity import PaymentEntity
from src.infrastructure.messaging.order_subscriber import OrderSubscriber


@patch(
    "src.infrastructure.messaging.order_subscriber.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_order_subscriber_initialization(mock_connect):
    payment_service = MagicMock()
    subscriber = OrderSubscriber(payment_service=payment_service)

    assert subscriber.payment_service == payment_service
    mock_connect.assert_called_once()


@patch(
    "src.infrastructure.messaging.order_subscriber.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_start_consuming(mock_connect):
    payment_service = MagicMock()
    subscriber = OrderSubscriber(payment_service=payment_service)
    subscriber.channel = MagicMock()

    subscriber.start_consuming()

    subscriber.channel.exchange_declare.assert_called_once_with(
        exchange="orders_exchange", exchange_type="topic", durable=True
    )
    subscriber.channel.queue_declare.assert_called_once_with(
        queue="orders_queue", durable=True
    )
    subscriber.channel.queue_bind.assert_called_once_with(
        exchange="orders_exchange",
        queue="orders_queue",
        routing_key="orders_queue",
    )
    subscriber.channel.basic_consume.assert_called_once_with(
        queue="orders_queue",
        on_message_callback=subscriber.on_message,
        auto_ack=False,
    )
    subscriber.channel.start_consuming.assert_called_once()


@patch(
    "src.infrastructure.messaging.order_subscriber.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_on_message_cancel_order(mock_connect):
    payment_service = MagicMock()
    subscriber = OrderSubscriber(payment_service=payment_service)
    subscriber.channel = MagicMock()

    payment_entity = PaymentEntity(order_id=1, amount=100.0, status="pending")
    payment_service.get_payment_by_order_id.return_value = payment_entity

    body = json.dumps(
        {"order_id": 1, "status": "canceled", "amount": 100.0}
    ).encode("utf-8")
    method = MagicMock()
    properties = MagicMock()

    subscriber.on_message(subscriber.channel, method, properties, body)

    payment_service.get_payment_by_order_id.assert_called_once_with(1)
    payment_service.cancel_payment.assert_called_once_with(payment_entity.id)
    subscriber.channel.basic_ack.assert_called_once_with(
        delivery_tag=method.delivery_tag
    )


@patch(
    "src.infrastructure.messaging.order_subscriber.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_on_message_create_payment(mock_connect):
    payment_service = MagicMock()
    subscriber = OrderSubscriber(payment_service=payment_service)
    subscriber.channel = MagicMock()

    body = json.dumps(
        {"order_id": 1, "status": "confirmed", "amount": 100.0}
    ).encode("utf-8")
    method = MagicMock()
    properties = MagicMock()

    subscriber.on_message(subscriber.channel, method, properties, body)

    payment_service.create_payment.assert_called_once_with(
        order_id=1, amount=100.0, status="pending"
    )
    subscriber.channel.basic_ack.assert_called_once_with(
        delivery_tag=method.delivery_tag
    )


@patch("src.infrastructure.messaging.order_subscriber.logger")
@patch(
    "src.infrastructure.messaging.order_subscriber.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_on_message_with_exception(mock_connect, mock_logger):
    payment_service = MagicMock()
    subscriber = OrderSubscriber(payment_service=payment_service)
    subscriber.channel = MagicMock()

    # Simulate a malformed message
    body = b"malformed message"
    method = MagicMock()
    properties = MagicMock()

    subscriber.on_message(subscriber.channel, method, properties, body)

    mock_logger.error.assert_called_once()
    subscriber.channel.basic_ack.assert_called_once_with(
        delivery_tag=method.delivery_tag
    )
