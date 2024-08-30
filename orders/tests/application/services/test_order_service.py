from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.application.services.order_service import OrderService
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidEntity,
)
from src.infrastructure.messaging.inventory_publisher import InventoryPublisher
from src.infrastructure.messaging.order_update_publisher import (
    OrderUpdatePublisher,
)


@pytest.fixture
def mock_order_repository():
    return MagicMock()


@pytest.fixture
def mock_customer_repository():
    return MagicMock()


@pytest.fixture
def mock_inventory_publisher():
    return MagicMock(spec=InventoryPublisher)


@pytest.fixture
def mock_order_update_publisher():
    return MagicMock(spec=OrderUpdatePublisher)


@pytest.fixture
def order_service(
    mock_order_repository,
    mock_customer_repository,
    mock_inventory_publisher,
    mock_order_update_publisher,
):
    return OrderService(
        order_repository=mock_order_repository,
        customer_repository=mock_customer_repository,
        inventory_publisher=mock_inventory_publisher,
        order_update_publisher=mock_order_update_publisher,
    )


@pytest.mark.asyncio
@patch("src.application.services.order_service.aiohttp.ClientSession.get")
async def test_create_order_insufficient_inventory(mock_get, order_service):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    order_items = [OrderItemEntity(product_sku="SKU123", quantity=10)]

    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value={"quantity": 5}
    )

    with pytest.raises(Exception):
        await order_service.create_order(customer, order_items)


@pytest.mark.asyncio
@patch("src.application.services.order_service.aiohttp.ClientSession.get")
async def test_update_order_insufficient_inventory(mock_get, order_service):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    order_items = [OrderItemEntity(product_sku="SKU123", quantity=10)]
    existing_order = OrderEntity(
        id=1, customer=customer, order_items=order_items
    )

    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value={"quantity": 5}
    )

    with pytest.raises(Exception):
        await order_service.update_order(1, customer, order_items)


@pytest.mark.asyncio
@patch("src.application.services.order_service.aiohttp.ClientSession.get")
async def test_calculate_order_total(mock_get, order_service):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    order_items = [OrderItemEntity(product_sku="SKU123", quantity=2)]
    existing_order = OrderEntity(
        id=1, customer=customer, order_items=order_items
    )

    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json = AsyncMock(
        return_value={"price": 10.0}
    )

    total = await order_service.calculate_order_total(existing_order)

    assert total == 20.0


def test_create_customer(order_service, mock_customer_repository):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    mock_customer_repository.find_by_email.return_value = None

    created_customer = order_service.create_customer(customer)

    assert created_customer is not None
    assert mock_customer_repository.save.called


def test_delete_customer(order_service, mock_customer_repository):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    mock_customer_repository.find_by_email.return_value = customer

    order_service.delete_customer("john.doe@example.com")

    assert mock_customer_repository.delete.called
