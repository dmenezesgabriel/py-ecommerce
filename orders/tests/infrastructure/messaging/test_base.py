import socket
import time
from unittest.mock import MagicMock, Mock, patch

import pika
import pytest
from src.infrastructure.messaging.base import BaseMessagingAdapter


@pytest.fixture
def connection_params():
    return Mock(spec=pika.ConnectionParameters)


@pytest.fixture
def base_messaging_adapter(connection_params):
    with patch.object(BaseMessagingAdapter, "connect", return_value=None):
        return BaseMessagingAdapter(connection_params)


def test_init_calls_connect(connection_params):
    with patch.object(BaseMessagingAdapter, "connect") as mock_connect:
        BaseMessagingAdapter(connection_params)
        mock_connect.assert_called_once()


def test_connect_successful_connection(connection_params):
    # Arrange
    mock_connection = MagicMock()
    mock_channel = MagicMock()

    with patch(
        "pika.BlockingConnection", return_value=mock_connection
    ) as mock_blocking_conn:
        mock_connection.channel.return_value = mock_channel

        # Act
        adapter = BaseMessagingAdapter(connection_params)

        # Assert
        mock_blocking_conn.assert_called_once_with(connection_params)
        mock_connection.channel.assert_called_once()
        assert adapter.connection == mock_connection
        assert adapter.channel == mock_channel


def test_connect_retries_on_failure(connection_params):
    # Arrange
    with patch(
        "pika.BlockingConnection",
        side_effect=pika.exceptions.AMQPConnectionError,
    ) as mock_blocking_conn:
        with patch("time.sleep") as mock_sleep:

            # Act
            with pytest.raises(pika.exceptions.AMQPConnectionError):
                BaseMessagingAdapter(connection_params, max_retries=3, delay=1)

            # Assert
            assert mock_blocking_conn.call_count == 3
            assert mock_sleep.call_count == 3


def test_connect_socket_gaierror(connection_params):
    # Arrange
    with patch(
        "pika.BlockingConnection", side_effect=socket.gaierror
    ) as mock_blocking_conn:
        with patch("time.sleep") as mock_sleep:

            # Act
            with pytest.raises(pika.exceptions.AMQPConnectionError):
                BaseMessagingAdapter(connection_params, max_retries=3, delay=1)

            # Assert
            assert mock_blocking_conn.call_count == 3
            assert mock_sleep.call_count == 3


def test_connect_logs_error_on_failure(connection_params):
    # Arrange
    with patch(
        "pika.BlockingConnection",
        side_effect=pika.exceptions.AMQPConnectionError,
    ):
        with patch("time.sleep"):
            with patch(
                "src.infrastructure.messaging.base.logger"
            ) as mock_logger:

                # Act
                with pytest.raises(pika.exceptions.AMQPConnectionError):
                    BaseMessagingAdapter(
                        connection_params, max_retries=3, delay=1
                    )

                # Assert
                assert mock_logger.error.call_count == 4


def test_connect_max_retries_exceeded(connection_params):
    # Arrange
    with patch(
        "pika.BlockingConnection",
        side_effect=pika.exceptions.AMQPConnectionError,
    ):
        with patch("time.sleep"):

            # Act & Assert
            with pytest.raises(pika.exceptions.AMQPConnectionError) as excinfo:
                BaseMessagingAdapter(connection_params, max_retries=2, delay=1)

            assert str(excinfo.value) == (
                "Failed to connect to RabbitMQ after multiple attempts."
            )


def test_exchange_name_initially_none(base_messaging_adapter):
    assert base_messaging_adapter.exchange_name is None
