import json
from unittest.mock import MagicMock, patch

import pika
import pytest
from src.infrastructure.messaging.payment_publisher import PaymentPublisher


@patch(
    "src.infrastructure.messaging.payment_publisher.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_payment_publisher_initialization(mock_connect):
    connection_params = pika.ConnectionParameters(host="localhost")
    publisher = PaymentPublisher(connection_params)

    assert publisher.exchange_name == "payment_exchange"
    mock_connect.assert_called_once()


@patch(
    "src.infrastructure.messaging.payment_publisher.BaseMessagingAdapter.connect",
    return_value=None,
)
def test_publish_payment_update_success(mock_connect):
    connection_params = pika.ConnectionParameters(host="localhost")
    publisher = PaymentPublisher(connection_params)
    publisher.channel = MagicMock()

    publisher.publish_payment_update("1", 1, "completed")

    expected_message = json.dumps(
        {
            "payment_id": "1",
            "order_id": 1,
            "status": "completed",
        }
    )

    publisher.channel.basic_publish.assert_called_once_with(
        exchange="payment_exchange",
        routing_key="payment_queue",
        body=expected_message,
    )


@patch(
    "src.infrastructure.messaging.payment_publisher.BaseMessagingAdapter.connect",
    return_value=None,
)
@patch("src.infrastructure.messaging.payment_publisher.logger")
def test_publish_payment_update_logs_success(mock_logger, mock_connect):
    connection_params = pika.ConnectionParameters(host="localhost")
    publisher = PaymentPublisher(connection_params)
    publisher.channel = MagicMock()

    publisher.publish_payment_update("1", 1, "completed")

    expected_message = json.dumps(
        {
            "payment_id": "1",
            "order_id": 1,
            "status": "completed",
        }
    )

    mock_logger.info.assert_called_once_with(
        f"Published payment update: {expected_message} to payment_queue"
    )
