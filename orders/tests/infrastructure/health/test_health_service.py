from unittest.mock import MagicMock, patch

from src.infrastructure.health.health_service import HealthService


def test_check_database_success():
    # Mock the database session
    mock_db = MagicMock()
    health_service = HealthService(db=mock_db, rabbitmq_host="localhost")

    # Ensure check_database returns True when the query succeeds
    assert health_service.check_database() is True
    mock_db.execute.assert_called_once()


def test_check_database_failure():
    # Mock the database session to raise an exception
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("DB Error")
    health_service = HealthService(db=mock_db, rabbitmq_host="localhost")

    # Ensure check_database returns False when the query fails
    assert health_service.check_database() is False
    mock_db.execute.assert_called_once()


@patch("src.infrastructure.health.health_service.pika.BlockingConnection")
def test_check_rabbitmq_success(mock_blocking_connection):
    # Mock the pika connection to close successfully
    mock_connection = MagicMock()
    mock_blocking_connection.return_value = mock_connection
    health_service = HealthService(db=MagicMock(), rabbitmq_host="localhost")

    # Ensure check_rabbitmq returns True when the connection succeeds
    assert health_service.check_rabbitmq() is True
    mock_blocking_connection.assert_called_once()
    mock_connection.close.assert_called_once()


@patch("src.infrastructure.health.health_service.pika.BlockingConnection")
def test_check_rabbitmq_failure(mock_blocking_connection):
    # Mock the pika connection to raise an exception
    mock_blocking_connection.side_effect = Exception("RabbitMQ Error")
    health_service = HealthService(db=MagicMock(), rabbitmq_host="localhost")

    # Ensure check_rabbitmq returns False when the connection fails
    assert health_service.check_rabbitmq() is False
    mock_blocking_connection.assert_called_once()


@patch.object(HealthService, "check_database", return_value=True)
@patch.object(HealthService, "check_rabbitmq", return_value=True)
def test_get_health_status_healthy(mock_check_db, mock_check_rabbitmq):
    health_service = HealthService(db=MagicMock(), rabbitmq_host="localhost")

    # Ensure get_health_status returns healthy status for both services
    status = health_service.get_health_status()
    assert status == {"database": "healthy", "rabbitmq": "healthy"}
    mock_check_db.assert_called_once()
    mock_check_rabbitmq.assert_called_once()


@patch.object(HealthService, "check_database", return_value=False)
@patch.object(HealthService, "check_rabbitmq", return_value=False)
def test_get_health_status_unhealthy(mock_check_db, mock_check_rabbitmq):
    health_service = HealthService(db=MagicMock(), rabbitmq_host="localhost")

    # Ensure get_health_status returns unhealthy status for both services
    status = health_service.get_health_status()
    assert status == {"database": "unhealthy", "rabbitmq": "unhealthy"}
    mock_check_db.assert_called_once()
    mock_check_rabbitmq.assert_called_once()
