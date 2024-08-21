import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from src.domain.entities.order_entity import OrderStatus
from src.infrastructure.messaging.delivery_subscriber import DeliverySubscriber


@pytest.fixture
def order_service():
    return Mock()


@pytest.fixture
def connection_params():
    return Mock()


@pytest.fixture
def delivery_subscriber(order_service, connection_params):
    with patch.object(DeliverySubscriber, "connect", return_value=None):
        return DeliverySubscriber(order_service, connection_params)


def test_start_consuming(delivery_subscriber):
    # Arrange
    delivery_subscriber.channel = MagicMock()

    # Act
    delivery_subscriber.start_consuming()

    # Assert
    delivery_subscriber.channel.exchange_declare.assert_called_once_with(
        exchange="delivery_exchange", exchange_type="topic", durable=True
    )
    delivery_subscriber.channel.queue_declare.assert_called_once_with(
        queue="delivery_queue", durable=True
    )
    delivery_subscriber.channel.queue_bind.assert_called_once_with(
        exchange="delivery_exchange",
        queue="delivery_queue",
        routing_key="delivery_queue",
    )
    delivery_subscriber.channel.basic_consume.assert_called_once_with(
        queue="delivery_queue",
        on_message_callback=delivery_subscriber.on_message,
        auto_ack=False,
    )
    delivery_subscriber.channel.start_consuming.assert_called_once()
    delivery_subscriber.channel.start_consuming.assert_called_once()


def test_on_message_shipped_status(delivery_subscriber, order_service):
    # Arrange
    ch = Mock()
    method = Mock()
    properties = Mock()
    body = json.dumps({"order_id": 1, "status": "in_transit"}).encode("utf-8")

    # Act
    delivery_subscriber.on_message(ch, method, properties, body)

    # Assert
    order_service.update_order_status.assert_called_once_with(
        1, OrderStatus.SHIPPED
    )
    ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


def test_on_message_delivered_status(delivery_subscriber, order_service):
    # Arrange
    ch = Mock()
    method = Mock()
    properties = Mock()
    body = json.dumps({"order_id": 2, "status": "delivered"}).encode("utf-8")

    # Act
    delivery_subscriber.on_message(ch, method, properties, body)

    # Assert
    order_service.update_order_status.assert_called_once_with(
        2, OrderStatus.DELIVERED
    )
    ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


def test_on_message_invalid_json(delivery_subscriber):
    # Arrange
    ch = Mock()
    method = Mock()
    properties = Mock()
    body = b"invalid json"

    with patch(
        "src.infrastructure.messaging.delivery_subscriber.logger"
    ) as mock_logger:
        # Act
        delivery_subscriber.on_message(ch, method, properties, body)

        # Assert
        mock_logger.error.assert_called_once()
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)


def test_on_message_exception_handling(delivery_subscriber):
    # Arrange
    ch = Mock()
    method = Mock()
    properties = Mock()
    body = json.dumps({"order_id": 3, "status": "unknown_status"}).encode(
        "utf-8"
    )

    with patch.object(
        delivery_subscriber.order_service,
        "update_order_status",
        side_effect=Exception("Test exception"),
    ):
        # Act
        delivery_subscriber.on_message(ch, method, properties, body)

        # Assert
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
