import json
from unittest.mock import MagicMock, patch

from src.domain.entities.order_entity import OrderStatus
from src.infrastructure.messaging.delivery_subscriber import DeliverySubscriber


@patch(
    "src.infrastructure.messaging.delivery_subscriber.BaseMessagingAdapter.connect"
)
def test_delivery_subscriber_initialization(mock_connect):
    mock_order_service = MagicMock()
    mock_connection_params = MagicMock()

    subscriber = DeliverySubscriber(
        order_service=mock_order_service,
        connection_params=mock_connection_params,
    )

    assert subscriber.order_service == mock_order_service
    mock_connect.assert_called_once()


@patch(
    "src.infrastructure.messaging.delivery_subscriber.BaseMessagingAdapter.connect"
)
def test_start_consuming(mock_connect):
    mock_order_service = MagicMock()
    mock_connection_params = MagicMock()

    subscriber = DeliverySubscriber(
        order_service=mock_order_service,
        connection_params=mock_connection_params,
    )

    subscriber.channel = MagicMock()
    subscriber.start_consuming()

    subscriber.channel.exchange_declare.assert_called_once_with(
        exchange="delivery_exchange", exchange_type="topic", durable=True
    )
    subscriber.channel.queue_declare.assert_called_once_with(
        queue="delivery_queue", durable=True
    )
    subscriber.channel.queue_bind.assert_called_once_with(
        exchange="delivery_exchange",
        queue="delivery_queue",
        routing_key="delivery_queue",
    )
    subscriber.channel.basic_consume.assert_called_once_with(
        queue="delivery_queue",
        on_message_callback=subscriber.on_message,
        auto_ack=False,
    )
    subscriber.channel.start_consuming.assert_called_once()


@patch(
    "src.infrastructure.messaging.delivery_subscriber.BaseMessagingAdapter.connect"
)
@patch("src.infrastructure.messaging.delivery_subscriber.asyncio.run")
def test_on_message_in_transit(mock_asyncio_run, mock_connect):
    mock_order_service = MagicMock()
    mock_connection_params = MagicMock()

    subscriber = DeliverySubscriber(
        order_service=mock_order_service,
        connection_params=mock_connection_params,
    )

    ch_mock = MagicMock()
    method_mock = MagicMock()
    properties_mock = MagicMock()

    body = json.dumps({"order_id": 1, "status": "in_transit"}).encode("utf-8")
    subscriber.on_message(ch_mock, method_mock, properties_mock, body)

    mock_asyncio_run.assert_called_once_with(
        mock_order_service.update_order_status(1, OrderStatus.SHIPPED)
    )
    ch_mock.basic_ack.assert_called_once_with(
        delivery_tag=method_mock.delivery_tag
    )


@patch(
    "src.infrastructure.messaging.delivery_subscriber.BaseMessagingAdapter.connect"
)
@patch("src.infrastructure.messaging.delivery_subscriber.asyncio.run")
def test_on_message_delivered(mock_asyncio_run, mock_connect):
    mock_order_service = MagicMock()
    mock_connection_params = MagicMock()

    subscriber = DeliverySubscriber(
        order_service=mock_order_service,
        connection_params=mock_connection_params,
    )

    ch_mock = MagicMock()
    method_mock = MagicMock()
    properties_mock = MagicMock()

    body = json.dumps({"order_id": 1, "status": "delivered"}).encode("utf-8")
    subscriber.on_message(ch_mock, method_mock, properties_mock, body)

    mock_asyncio_run.assert_called_once_with(
        mock_order_service.update_order_status(1, OrderStatus.FINISHED)
    )
    ch_mock.basic_ack.assert_called_once_with(
        delivery_tag=method_mock.delivery_tag
    )


@patch(
    "src.infrastructure.messaging.delivery_subscriber.BaseMessagingAdapter.connect"
)
def test_on_message_exception(mock_connect):
    mock_order_service = MagicMock()
    mock_connection_params = MagicMock()

    subscriber = DeliverySubscriber(
        order_service=mock_order_service,
        connection_params=mock_connection_params,
    )

    ch_mock = MagicMock()
    method_mock = MagicMock()
    properties_mock = MagicMock()

    # Simulate an invalid JSON in the body
    body = b"invalid json"
    subscriber.on_message(ch_mock, method_mock, properties_mock, body)

    ch_mock.basic_ack.assert_called_once_with(
        delivery_tag=method_mock.delivery_tag
    )
