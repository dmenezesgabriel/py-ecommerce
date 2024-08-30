import socket
from unittest.mock import MagicMock, patch

import pika
import pytest
from src.infrastructure.messaging.base import BaseMessagingAdapter


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.time.sleep")
def test_connect_success(mock_sleep, mock_blocking_connection):
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_blocking_connection.return_value = mock_connection

    connection_params = MagicMock()
    adapter = BaseMessagingAdapter(connection_params)

    mock_blocking_connection.assert_called_once_with(connection_params)
    assert adapter.connection == mock_connection
    assert adapter.channel == mock_channel
    assert mock_sleep.call_count == 0  # Ensure no retries were needed


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.time.sleep")
def test_connect_failure_retries(mock_sleep, mock_blocking_connection):
    mock_blocking_connection.side_effect = pika.exceptions.AMQPConnectionError

    connection_params = MagicMock()
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        BaseMessagingAdapter(connection_params, max_retries=3, delay=1)

    assert mock_blocking_connection.call_count == 3
    assert (
        mock_sleep.call_count == 3
    )  # Ensure the sleep is called for each retry


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.time.sleep")
def test_connect_failure_due_to_socket_error(
    mock_sleep, mock_blocking_connection
):
    mock_blocking_connection.side_effect = socket.gaierror

    connection_params = MagicMock()
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        BaseMessagingAdapter(connection_params, max_retries=3, delay=1)

    assert mock_blocking_connection.call_count == 3
    assert (
        mock_sleep.call_count == 3
    )  # Ensure the sleep is called for each retry


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
@patch("src.infrastructure.messaging.base.time.sleep")
def test_connect_failure_exceeds_max_retries(
    mock_sleep, mock_blocking_connection
):
    mock_blocking_connection.side_effect = pika.exceptions.AMQPConnectionError

    connection_params = MagicMock()
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        BaseMessagingAdapter(connection_params, max_retries=5, delay=1)

    assert mock_blocking_connection.call_count == 5
    assert (
        mock_sleep.call_count == 5
    )  # Ensure the sleep is called for each retry


@patch("src.infrastructure.messaging.base.pika.BlockingConnection")
def test_connect_sets_channel_and_connection(mock_blocking_connection):
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_blocking_connection.return_value = mock_connection

    connection_params = MagicMock()
    adapter = BaseMessagingAdapter(connection_params)

    assert adapter.connection == mock_connection
    assert adapter.channel == mock_channel
    mock_blocking_connection.assert_called_once_with(connection_params)


@patch(
    "src.infrastructure.messaging.base.pika.BlockingConnection",
    side_effect=pika.exceptions.AMQPConnectionError,
)
@patch("src.infrastructure.messaging.base.time.sleep")
def test_connect_raises_exception_after_retries(
    mock_sleep, mock_blocking_connection
):
    connection_params = MagicMock()

    with pytest.raises(
        pika.exceptions.AMQPConnectionError,
        match="Failed to connect to RabbitMQ after multiple attempts.",
    ):
        BaseMessagingAdapter(connection_params, max_retries=3, delay=1)

    assert mock_blocking_connection.call_count == 3
    assert mock_sleep.call_count == 3
