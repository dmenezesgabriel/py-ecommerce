import json
from unittest.mock import MagicMock, patch

import pytest
from src.infrastructure.messaging.payment_subscriber import PaymentSubscriber


@pytest.fixture
def mock_order_service():
    return MagicMock()


@pytest.fixture
def mock_connection_params():
    return MagicMock()


@pytest.fixture
def payment_subscriber(mock_order_service, mock_connection_params):
    with patch(
        "src.infrastructure.messaging.payment_subscriber.BaseMessagingAdapter.__init__"
    ):
        return PaymentSubscriber(
            order_service=mock_order_service,
            connection_params=mock_connection_params,
        )


def test_start_consuming(payment_subscriber):
    payment_subscriber.channel = MagicMock()

    payment_subscriber.start_consuming()

    payment_subscriber.channel.exchange_declare.assert_called_once_with(
        exchange="payment_exchange", exchange_type="topic", durable=True
    )
    payment_subscriber.channel.queue_declare.assert_called_once_with(
        queue="payment_queue", durable=True
    )
    payment_subscriber.channel.queue_bind.assert_called_once_with(
        exchange="payment_exchange",
        queue="payment_queue",
        routing_key="payment_queue",
    )
    payment_subscriber.channel.basic_consume.assert_called_once_with(
        queue="payment_queue",
        on_message_callback=payment_subscriber.on_message,
        auto_ack=False,
    )
    payment_subscriber.channel.start_consuming.assert_called_once()


@patch("src.infrastructure.messaging.payment_subscriber.asyncio.run")
def test_on_message_completed(
    mock_asyncio_run, payment_subscriber, mock_order_service
):
    payment_subscriber.channel = MagicMock()
    ch = MagicMock()
    method = MagicMock()
    properties = MagicMock()

    body = json.dumps({"order_id": 1, "status": "completed"}).encode("utf-8")

    payment_subscriber.on_message(ch, method, properties, body)

    mock_order_service.set_paid_order.assert_called_once_with(1)
    mock_asyncio_run.assert_called_once_with(
        mock_order_service.set_paid_order(1)
    )
    ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


@patch("src.infrastructure.messaging.payment_subscriber.asyncio.run")
def test_on_message_canceled(
    mock_asyncio_run, payment_subscriber, mock_order_service
):
    payment_subscriber.channel = MagicMock()
    ch = MagicMock()
    method = MagicMock()
    properties = MagicMock()

    body = json.dumps({"order_id": 2, "status": "canceled"}).encode("utf-8")

    payment_subscriber.on_message(ch, method, properties, body)

    mock_order_service.cancel_order.assert_called_once_with(2)
    mock_asyncio_run.assert_called_once_with(
        mock_order_service.cancel_order(2)
    )
    ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


@patch("src.infrastructure.messaging.payment_subscriber.asyncio.run")
def test_on_message_refunded(
    mock_asyncio_run, payment_subscriber, mock_order_service
):
    payment_subscriber.channel = MagicMock()
    ch = MagicMock()
    method = MagicMock()
    properties = MagicMock()

    body = json.dumps({"order_id": 3, "status": "refunded"}).encode("utf-8")

    payment_subscriber.on_message(ch, method, properties, body)

    mock_order_service.cancel_order.assert_called_once_with(3)
    mock_asyncio_run.assert_called_once_with(
        mock_order_service.cancel_order(3)
    )
    ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


def test_on_message_invalid_json(payment_subscriber):
    payment_subscriber.channel = MagicMock()
    ch = MagicMock()
    method = MagicMock()
    properties = MagicMock()

    invalid_body = b"Invalid JSON"

    with patch(
        "src.infrastructure.messaging.payment_subscriber.logger"
    ) as mock_logger:
        payment_subscriber.on_message(ch, method, properties, invalid_body)

        mock_logger.error.assert_called_once()
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
