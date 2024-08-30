import time
from unittest.mock import MagicMock, call, patch

import pika
import pytest
from src.infrastructure.messaging.base import BaseMessagingAdapter


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.logger")
@patch("src.infrastructure.messaging.base.time.sleep", return_value=None)
def test_connect_success(mock_sleep, mock_logger, mock_blocking_connection):
    # Mock successful connection
    mock_connection = MagicMock()
    mock_blocking_connection.return_value = mock_connection

    connection_params = MagicMock()
    adapter = BaseMessagingAdapter(connection_params)

    mock_blocking_connection.assert_called_once_with(connection_params)
    assert adapter.connection == mock_connection
    assert adapter.channel == mock_connection.channel.return_value
    mock_logger.error.assert_not_called()
    mock_sleep.assert_not_called()


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.logger")
@patch("src.infrastructure.messaging.base.time.sleep", return_value=None)
def test_connect_failure_then_success(
    mock_sleep, mock_logger, mock_blocking_connection
):
    # Mock connection failure followed by success
    mock_connection = MagicMock()
    mock_blocking_connection.side_effect = [
        pika.exceptions.AMQPConnectionError("Connection failed"),
        mock_connection,
    ]

    connection_params = MagicMock()
    adapter = BaseMessagingAdapter(connection_params)

    assert mock_blocking_connection.call_count == 2
    assert adapter.connection == mock_connection
    assert adapter.channel == mock_connection.channel.return_value
    mock_logger.error.assert_called_once_with(
        "Attempt 1/5 to connect to RabbitMQ failed: Connection failed"
    )
    mock_sleep.assert_called_once_with(5)


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.logger")
@patch("src.infrastructure.messaging.base.time.sleep", return_value=None)
def test_connect_failure_max_retries(
    mock_sleep, mock_logger, mock_blocking_connection
):
    # Mock connection failure for all attempts
    mock_blocking_connection.side_effect = pika.exceptions.AMQPConnectionError(
        "Connection failed"
    )

    connection_params = MagicMock()
    with pytest.raises(
        pika.exceptions.AMQPConnectionError,
        match="Failed to connect to RabbitMQ after multiple attempts.",
    ):
        BaseMessagingAdapter(connection_params)

    assert mock_blocking_connection.call_count == 5
    assert (
        mock_logger.error.call_count == 6
    )  # 5 attempts + final failure message
    mock_sleep.assert_called_with(5)


def test_adapter_initialization():
    connection_params = MagicMock()
    with patch.object(
        BaseMessagingAdapter, "connect", return_value=None
    ) as mock_connect:
        adapter = BaseMessagingAdapter(
            connection_params, max_retries=3, delay=2
        )
        assert adapter.connection_params == connection_params
        assert adapter.max_retries == 3
        assert adapter.delay == 2
        mock_connect.assert_called_once()


@patch(
    "src.infrastructure.messaging.base.pika.BlockingConnection",
    side_effect=pika.exceptions.AMQPConnectionError("Connection failed"),
)
@patch("src.infrastructure.messaging.base.logger")
@patch("src.infrastructure.messaging.base.time.sleep", return_value=None)
def test_connect_logging(mock_sleep, mock_logger, mock_blocking_connection):
    connection_params = MagicMock()
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        BaseMessagingAdapter(connection_params)

    expected_calls = [
        call("Attempt 1/5 to connect to RabbitMQ failed: Connection failed"),
        call("Attempt 2/5 to connect to RabbitMQ failed: Connection failed"),
        call("Attempt 3/5 to connect to RabbitMQ failed: Connection failed"),
        call("Attempt 4/5 to connect to RabbitMQ failed: Connection failed"),
        call("Attempt 5/5 to connect to RabbitMQ failed: Connection failed"),
        call("Max retries exceeded. Could not connect to RabbitMQ."),
    ]
    mock_logger.error.assert_has_calls(expected_calls, any_order=False)
