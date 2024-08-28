import unittest
from unittest.mock import MagicMock, patch

import pika
from src.infrastructure.messaging.delivery_publisher import DeliveryPublisher


class TestDeliveryPublisher(unittest.TestCase):
    def setUp(self):
        self.connection_params = pika.ConnectionParameters("localhost")

    @patch(
        "src.infrastructure.messaging.delivery_publisher.pika.BlockingConnection"
    )
    @patch("src.infrastructure.messaging.delivery_publisher.logger")
    def test_connect_success(self, mock_logger, mock_blocking_connection):
        # Arrange
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_blocking_connection.return_value = mock_connection

        # Act
        publisher = DeliveryPublisher(
            connection_params=self.connection_params, max_retries=3, delay=1
        )

        # Assert
        mock_blocking_connection.assert_called_once_with(
            self.connection_params
        )
        self.assertIsNotNone(publisher.channel)
        mock_logger.error.assert_not_called()

    @patch(
        "src.infrastructure.messaging.delivery_publisher.pika.BlockingConnection"
    )
    @patch("src.infrastructure.messaging.delivery_publisher.logger")
    @patch("time.sleep", return_value=None)
    def test_connect_failure(
        self, mock_sleep, mock_logger, mock_blocking_connection
    ):
        # Arrange
        mock_blocking_connection.side_effect = (
            pika.exceptions.AMQPConnectionError
        )

        # Act & Assert
        with self.assertRaises(pika.exceptions.AMQPConnectionError):
            DeliveryPublisher(
                connection_params=self.connection_params,
                max_retries=3,
                delay=1,
            )

        self.assertEqual(mock_blocking_connection.call_count, 3)
        mock_logger.error.assert_called_with(
            "Max retries exceeded. Could not connect to RabbitMQ."
        )
        mock_sleep.assert_called_with(1)

    @patch(
        "src.infrastructure.messaging.delivery_publisher.pika.BlockingConnection"
    )
    @patch("src.infrastructure.messaging.delivery_publisher.logger")
    def test_publish_delivery_update_success(
        self, mock_logger, mock_blocking_connection
    ):
        # Arrange
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_blocking_connection.return_value = mock_connection

        publisher = DeliveryPublisher(
            connection_params=self.connection_params, max_retries=3, delay=1
        )

        # Act
        publisher.publish_delivery_update(1, 101, "delivered")

        # Assert
        mock_channel.basic_publish.assert_called_once_with(
            exchange=publisher.exchange_name,
            routing_key="delivery_queue",
            body='{"delivery_id": 1, "order_id": 101, "status": "delivered"}',
        )
        mock_logger.info.assert_called_once_with(
            'Published delivery update: {"delivery_id": 1, "order_id": 101, "status": "delivered"} to delivery_queue'
        )


if __name__ == "__main__":
    unittest.main()
