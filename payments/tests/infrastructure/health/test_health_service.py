from unittest.mock import MagicMock, patch

import pika
import pytest
from pymongo.errors import ServerSelectionTimeoutError
from src.infrastructure.health.health_service import HealthService


def test_check_mongodb_success():
    # Mock the MongoDB database connection
    mock_db = MagicMock()
    mock_db.command.return_value = {"ok": 1}

    health_service = HealthService(mock_db, rabbitmq_host="localhost")

    assert health_service.check_mongodb() is True
    mock_db.command.assert_called_once_with("ping")


def test_check_mongodb_failure():
    # Mock the MongoDB database connection to raise an exception
    mock_db = MagicMock()
    mock_db.command.side_effect = ServerSelectionTimeoutError(
        "Failed to connect"
    )

    health_service = HealthService(mock_db, rabbitmq_host="localhost")

    assert health_service.check_mongodb() is False
    mock_db.command.assert_called_once_with("ping")


@patch("src.infrastructure.health.health_service.pika.BlockingConnection")
def test_check_rabbitmq_success(mock_blocking_connection):
    # Mock successful RabbitMQ connection
    mock_connection = MagicMock()
    mock_blocking_connection.return_value = mock_connection

    health_service = HealthService(db=None, rabbitmq_host="localhost")

    assert health_service.check_rabbitmq() is True
    mock_blocking_connection.assert_called_once_with(
        pika.ConnectionParameters(host="localhost", heartbeat=120)
    )
    mock_connection.close.assert_called_once()


@patch("src.infrastructure.health.health_service.pika.BlockingConnection")
def test_check_rabbitmq_failure(mock_blocking_connection):
    # Mock failed RabbitMQ connection
    mock_blocking_connection.side_effect = Exception("Connection failed")

    health_service = HealthService(db=None, rabbitmq_host="localhost")

    assert health_service.check_rabbitmq() is False
    mock_blocking_connection.assert_called_once_with(
        pika.ConnectionParameters(host="localhost", heartbeat=120)
    )


def test_get_health_status():
    # Mock the HealthService methods
    mock_db = MagicMock()
    health_service = HealthService(mock_db, rabbitmq_host="localhost")

    with patch.object(
        health_service, "check_mongodb", return_value=True
    ) as mock_check_mongodb, patch.object(
        health_service, "check_rabbitmq", return_value=True
    ) as mock_check_rabbitmq:

        health_status = health_service.get_health_status()
        assert health_status == {"mongodb": "healthy", "rabbitmq": "healthy"}
        mock_check_mongodb.assert_called_once()
        mock_check_rabbitmq.assert_called_once()

    with patch.object(
        health_service, "check_mongodb", return_value=False
    ) as mock_check_mongodb, patch.object(
        health_service, "check_rabbitmq", return_value=False
    ) as mock_check_rabbitmq:

        health_status = health_service.get_health_status()
        assert health_status == {
            "mongodb": "unhealthy",
            "rabbitmq": "unhealthy",
        }
        mock_check_mongodb.assert_called_once()
        mock_check_rabbitmq.assert_called_once()
