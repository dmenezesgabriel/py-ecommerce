import unittest
from unittest.mock import MagicMock, patch

import pika
from sqlalchemy.sql import text
from src.infrastructure.health.health_service import HealthService


class TestHealthService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.rabbitmq_host = "localhost"
        self.health_service = HealthService(self.mock_db, self.rabbitmq_host)

    @patch("src.infrastructure.health.health_service.logger")
    def test_check_database_success(self, mock_logger):
        # Arrange
        self.mock_db.execute.return_value = None

        # Act
        result = self.health_service.check_database()

        # Assert
        self.assertTrue(result)
        self.mock_db.execute.assert_called_once()
        # Check the SQL text used in the call
        sql_text_used = self.mock_db.execute.call_args[0][0]
        self.assertEqual(str(sql_text_used), str(text("SELECT 1")))
        mock_logger.error.assert_not_called()

    @patch("src.infrastructure.health.health_service.logger")
    def test_check_database_failure(self, mock_logger):
        # Arrange
        self.mock_db.execute.side_effect = Exception("DB Error")

        # Act
        result = self.health_service.check_database()

        # Assert
        self.assertFalse(result)
        self.mock_db.execute.assert_called_once()
        # Check the SQL text used in the call
        sql_text_used = self.mock_db.execute.call_args[0][0]
        self.assertEqual(str(sql_text_used), str(text("SELECT 1")))
        mock_logger.error.assert_called_once_with(
            "Database health check failed: DB Error"
        )

    @patch("src.infrastructure.health.health_service.pika.BlockingConnection")
    @patch("src.infrastructure.health.health_service.logger")
    def test_check_rabbitmq_success(self, mock_logger, mock_pika):
        # Arrange
        mock_connection = MagicMock()
        mock_pika.return_value = mock_connection

        # Act
        result = self.health_service.check_rabbitmq()

        # Assert
        self.assertTrue(result)
        mock_pika.assert_called_once_with(
            pika.ConnectionParameters(host=self.rabbitmq_host, heartbeat=120)
        )
        mock_connection.close.assert_called_once()
        mock_logger.error.assert_not_called()

    @patch("src.infrastructure.health.health_service.pika.BlockingConnection")
    @patch("src.infrastructure.health.health_service.logger")
    def test_check_rabbitmq_failure(self, mock_logger, mock_pika):
        # Arrange
        mock_pika.side_effect = Exception("RabbitMQ Error")

        # Act
        result = self.health_service.check_rabbitmq()

        # Assert
        self.assertFalse(result)
        mock_pika.assert_called_once_with(
            pika.ConnectionParameters(host=self.rabbitmq_host, heartbeat=120)
        )
        mock_logger.error.assert_called_once_with(
            "RabbitMQ health check failed: RabbitMQ Error"
        )

    @patch.object(HealthService, "check_database", return_value=True)
    @patch.object(HealthService, "check_rabbitmq", return_value=True)
    def test_get_health_status_healthy(
        self, mock_check_rabbitmq, mock_check_db
    ):
        # Act
        status = self.health_service.get_health_status()

        # Assert
        self.assertEqual(
            status, {"database": "healthy", "rabbitmq": "healthy"}
        )
        mock_check_db.assert_called_once()
        mock_check_rabbitmq.assert_called_once()

    @patch.object(HealthService, "check_database", return_value=False)
    @patch.object(HealthService, "check_rabbitmq", return_value=False)
    def test_get_health_status_unhealthy(
        self, mock_check_rabbitmq, mock_check_db
    ):
        # Act
        status = self.health_service.get_health_status()

        # Assert
        self.assertEqual(
            status, {"database": "unhealthy", "rabbitmq": "unhealthy"}
        )
        mock_check_db.assert_called_once()
        mock_check_rabbitmq.assert_called_once()


if __name__ == "__main__":
    unittest.main()
