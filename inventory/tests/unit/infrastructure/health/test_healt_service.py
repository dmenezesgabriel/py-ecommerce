from unittest.mock import MagicMock, Mock, patch

import pytest
from src.infrastructure.health.health_service import HealthService


class TestHealthService:

    @patch("src.infrastructure.health.health_service.Session")
    def test_check_database_success(self, mock_session):
        # Arrange
        mock_db = mock_session()
        mock_db.execute.return_value = None
        service = HealthService(db=mock_db, rabbitmq_host="localhost")

        # Act
        result = service.check_database()

        # Assert
        assert result is True
        mock_db.execute.assert_called_once()

    @patch("src.infrastructure.health.health_service.Session")
    def test_check_database_failure(self, mock_session):
        # Arrange
        mock_db = mock_session()
        mock_db.execute.side_effect = Exception("DB error")
        service = HealthService(db=mock_db, rabbitmq_host="localhost")

        # Act
        result = service.check_database()

        # Assert
        assert result is False
        mock_db.execute.assert_called_once()

    @patch("src.infrastructure.health.health_service.pika.BlockingConnection")
    def test_check_rabbitmq_success(self, mock_pika):
        # Arrange
        mock_connection = mock_pika.return_value
        service = HealthService(db=Mock(), rabbitmq_host="localhost")

        # Act
        result = service.check_rabbitmq()

        # Assert
        assert result is True
        mock_pika.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.infrastructure.health.health_service.pika.BlockingConnection")
    def test_check_rabbitmq_failure(self, mock_pika):
        # Arrange
        mock_pika.side_effect = Exception("RabbitMQ error")
        service = HealthService(db=Mock(), rabbitmq_host="localhost")

        # Act
        result = service.check_rabbitmq()

        # Assert
        assert result is False
        mock_pika.assert_called_once()

    @patch.object(HealthService, "check_database", return_value=True)
    @patch.object(HealthService, "check_rabbitmq", return_value=True)
    def test_get_health_status_healthy(
        self, mock_check_db, mock_check_rabbitmq
    ):
        # Arrange
        service = HealthService(db=Mock(), rabbitmq_host="localhost")

        # Act
        result = service.get_health_status()

        # Assert
        assert result == {"database": "healthy", "rabbitmq": "healthy"}
        mock_check_db.assert_called_once()
        mock_check_rabbitmq.assert_called_once()

    @patch.object(HealthService, "check_database", return_value=False)
    @patch.object(HealthService, "check_rabbitmq", return_value=False)
    def test_get_health_status_unhealthy(
        self, mock_check_db, mock_check_rabbitmq
    ):
        # Arrange
        service = HealthService(db=Mock(), rabbitmq_host="localhost")

        # Act
        result = service.get_health_status()

        # Assert
        assert result == {"database": "unhealthy", "rabbitmq": "unhealthy"}
        mock_check_db.assert_called_once()
        mock_check_rabbitmq.assert_called_once()


if __name__ == "__main__":
    pytest.main()
