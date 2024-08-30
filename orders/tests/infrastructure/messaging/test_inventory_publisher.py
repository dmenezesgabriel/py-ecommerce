from unittest.mock import MagicMock, call, patch

import pika
import pytest
from src.infrastructure.messaging.inventory_publisher import InventoryPublisher


@patch(
    "src.infrastructure.messaging.inventory_publisher.BaseMessagingAdapter.__init__"
)
def test_inventory_publisher_initialization(mock_base_init):
    # Mock BaseMessagingAdapter init
    mock_base_init.return_value = None

    connection_params = MagicMock()
    publisher = InventoryPublisher(connection_params)

    # Verify that the base class __init__ was called with the correct parameters
    mock_base_init.assert_called_once_with(connection_params, 5, 5)
    assert publisher.exchange_name == "inventory_exchange"


@patch(
    "src.infrastructure.messaging.inventory_publisher.BaseMessagingAdapter.connect"
)
@patch("src.infrastructure.messaging.inventory_publisher.logger")
@patch(
    "src.infrastructure.messaging.inventory_publisher.pika.BlockingConnection"
)
def test_publish_inventory_update_success(
    mock_blocking_connection, mock_logger, mock_connect
):
    mock_channel = MagicMock()
    mock_connection = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_blocking_connection.return_value = mock_connection

    connection_params = MagicMock()
    publisher = InventoryPublisher(connection_params)
    publisher.channel = mock_channel

    # Call the method to publish an inventory update
    publisher.publish_inventory_update(sku="SKU123", action="add", quantity=10)

    # Verify that basic_publish was called with the correct parameters
    mock_channel.basic_publish.assert_called_once_with(
        exchange="inventory_exchange",
        routing_key="inventory_queue",
        body='{"sku": "SKU123", "action": "add", "quantity": 10}',
    )
    mock_logger.info.assert_called_once_with(
        'Published inventory update: {"sku": "SKU123", "action": "add", "quantity": 10}'
    )
    mock_connect.assert_called_once()
