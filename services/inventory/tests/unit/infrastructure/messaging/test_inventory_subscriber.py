import json
import socket
from unittest.mock import Mock, patch

import pika
import pytest

from src.application.services.product_service import ProductService
from src.config import Config
from src.infrastructure.messaging.inventory_subscriber import (
    InventorySubscriber,
)


class TestInventorySubscriber:

    @patch("src.infrastructure.messaging.inventory_subscriber.time.sleep")
    @patch(
        "src.infrastructure.messaging.inventory_subscriber.pika.BlockingConnection"
    )
    def test_connect_success(self, mock_pika: Mock, mock_sleep: Mock) -> None:
        # Arrange
        mock_connection = Mock()
        mock_pika.return_value = mock_connection
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)

        # Act
        result = subscriber.connect()

        # Assert
        assert result is True
        mock_pika.assert_called_once_with(subscriber.connection_params)
        assert mock_sleep.call_count == 0

    @patch("src.infrastructure.messaging.inventory_subscriber.time.sleep")
    @patch(
        "src.infrastructure.messaging.inventory_subscriber.pika.BlockingConnection"
    )
    def test_connect_failure(self, mock_pika: Mock, mock_sleep: Mock) -> None:
        # Arrange
        mock_pika.side_effect = pika.exceptions.AMQPConnectionError
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)

        # Act
        result = subscriber.connect()

        # Assert
        assert result is False
        assert mock_pika.call_count == subscriber.max_retries
        assert mock_sleep.call_count == subscriber.max_retries

    @patch("src.infrastructure.messaging.inventory_subscriber.time.sleep")
    @patch(
        "src.infrastructure.messaging.inventory_subscriber.pika.BlockingConnection"
    )
    def test_connect_socket_failure(
        self, mock_pika: Mock, mock_sleep: Mock
    ) -> None:
        # Arrange
        mock_pika.side_effect = socket.gaierror
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)

        # Act
        result = subscriber.connect()

        # Assert
        assert result is False
        assert mock_pika.call_count == subscriber.max_retries
        assert mock_sleep.call_count == subscriber.max_retries

    @patch.object(InventorySubscriber, "connect", return_value=True)
    @patch(
        "src.infrastructure.messaging.inventory_subscriber.pika.BlockingConnection"
    )
    def test_start_consuming(
        self, mock_pika: Mock, mock_connect: Mock
    ) -> None:
        # Arrange
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)
        mock_channel = Mock()
        subscriber.channel = mock_channel  # Manually set the channel

        # Act
        subscriber.start_consuming()

        # Assert
        mock_connect.assert_called_once()
        mock_channel.exchange_declare.assert_called_once_with(
            exchange="inventory_exchange", exchange_type="direct", durable=True
        )
        mock_channel.queue_declare.assert_called_once_with(
            queue="inventory_queue", durable=True
        )
        mock_channel.queue_bind.assert_called_once_with(
            exchange="inventory_exchange",
            queue="inventory_queue",
            routing_key="inventory_queue",
        )
        mock_channel.basic_consume.assert_called_once_with(
            queue="inventory_queue",
            on_message_callback=subscriber.on_message,
            auto_ack=False,
        )
        mock_channel.start_consuming.assert_called_once()

    @patch.object(InventorySubscriber, "connect", return_value=False)
    def test_start_consuming_connection_failure(
        self, mock_connect: Mock
    ) -> None:
        # Arrange
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)

        # Act
        subscriber.start_consuming()

        # Assert
        mock_connect.assert_called_once()

    @patch.object(Config, "BROKER_HOST", "rabbitmq")
    @patch("src.infrastructure.messaging.inventory_subscriber.json.loads")
    def test_on_message_add_inventory(self, mock_json: Mock) -> None:
        # Arrange
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)
        mock_channel = Mock()
        mock_method = Mock()
        mock_body = json.dumps(
            {"sku": "123", "action": "add", "quantity": 50}
        ).encode("utf-8")

        mock_json.return_value.get.side_effect = ["123", "add", 50]

        # Act
        subscriber.on_message(mock_channel, mock_method, None, mock_body)

        # Assert
        product_service.add_inventory.assert_called_once_with("123", 50)
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag=mock_method.delivery_tag
        )

    @patch.object(Config, "BROKER_HOST", "rabbitmq")
    @patch("src.infrastructure.messaging.inventory_subscriber.json.loads")
    def test_on_message_subtract_inventory(self, mock_json: Mock) -> None:
        # Arrange
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)
        mock_channel = Mock()
        mock_method = Mock()
        mock_body = json.dumps(
            {"sku": "123", "action": "subtract", "quantity": 50}
        ).encode("utf-8")

        mock_json.return_value.get.side_effect = ["123", "subtract", 50]

        # Act
        subscriber.on_message(mock_channel, mock_method, None, mock_body)

        # Assert
        product_service.subtract_inventory.assert_called_once_with("123", 50)
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag=mock_method.delivery_tag
        )

    @patch(
        "src.infrastructure.messaging.inventory_subscriber.json.loads",
        side_effect=ValueError,
    )
    @patch("src.infrastructure.messaging.inventory_subscriber.logger")
    def test_on_message_processing_error(
        self, mock_logger: Mock, mock_json: Mock
    ) -> None:
        # Arrange
        product_service = Mock(spec=ProductService)
        subscriber = InventorySubscriber(product_service)
        mock_channel = Mock()
        mock_method = Mock()
        mock_body = b"invalid_json"

        # Act
        subscriber.on_message(mock_channel, mock_method, None, mock_body)

        # Assert
        mock_logger.error.assert_called_once()
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag=mock_method.delivery_tag
        )


if __name__ == "__main__":
    pytest.main()
