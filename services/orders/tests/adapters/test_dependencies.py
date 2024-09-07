from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session
from src.adapters.dependencies import (
    get_health_service,
    get_inventory_publisher,
    get_order_service,
    get_order_update_publisher,
)
from src.application.services.order_service import OrderService
from src.infrastructure.health.health_service import HealthService
from src.infrastructure.messaging.inventory_publisher import InventoryPublisher
from src.infrastructure.messaging.order_update_publisher import (
    OrderUpdatePublisher,
)
from src.infrastructure.persistence.sqlalchemy_customer_repository import (
    SQLAlchemyCustomerRepository,
)
from src.infrastructure.persistence.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository,
)


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_inventory_publisher():
    return MagicMock(spec=InventoryPublisher)


@pytest.fixture
def mock_order_update_publisher():
    return MagicMock(spec=OrderUpdatePublisher)


def test_get_health_service(mock_db_session):
    health_service = get_health_service(db=mock_db_session)
    assert isinstance(health_service, HealthService)
    assert health_service.db == mock_db_session


@patch("src.adapters.dependencies.pika.BlockingConnection")
@patch("src.adapters.dependencies.pika.ConnectionParameters")
def test_get_inventory_publisher(
    mock_connection_params, mock_blocking_connection
):
    mock_connection_params.return_value = MagicMock()
    mock_blocking_connection.return_value = MagicMock()
    inventory_publisher = get_inventory_publisher()
    assert isinstance(inventory_publisher, InventoryPublisher)
    mock_connection_params.assert_called_once_with(
        host="rabbitmq", heartbeat=120
    )
    mock_blocking_connection.assert_called_once()


@patch("src.adapters.dependencies.pika.BlockingConnection")
@patch("src.adapters.dependencies.pika.ConnectionParameters")
def test_get_order_update_publisher(
    mock_connection_params, mock_blocking_connection
):
    mock_connection_params.return_value = MagicMock()
    mock_blocking_connection.return_value = MagicMock()
    order_update_publisher = get_order_update_publisher()
    assert isinstance(order_update_publisher, OrderUpdatePublisher)
    mock_connection_params.assert_called_once_with(
        host="rabbitmq", heartbeat=120
    )
    mock_blocking_connection.assert_called_once()


@patch("src.adapters.dependencies.SQLAlchemyOrderRepository")
@patch("src.adapters.dependencies.SQLAlchemyCustomerRepository")
def test_get_order_service(
    mock_customer_repository,
    mock_order_repository,
    mock_db_session,
    mock_inventory_publisher,
    mock_order_update_publisher,
):
    mock_customer_repository.return_value = MagicMock()
    mock_order_repository.return_value = MagicMock()

    order_service = get_order_service(
        db=mock_db_session,
        inventory_publisher=mock_inventory_publisher,
        order_update_publisher=mock_order_update_publisher,
    )
    assert isinstance(order_service, OrderService)
    mock_order_repository.assert_called_once_with(mock_db_session)
    mock_customer_repository.assert_called_once_with(mock_db_session)
