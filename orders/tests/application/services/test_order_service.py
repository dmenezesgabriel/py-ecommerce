import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from src.application.services.order_service import OrderService
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidEntity,
)


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.fixture
def order_service():
    order_repo = Mock()
    customer_repo = Mock()
    inventory_pub = Mock()
    order_update_pub = Mock()
    return OrderService(
        order_repository=order_repo,
        customer_repository=customer_repo,
        inventory_publisher=inventory_pub,
        order_update_publisher=order_update_pub,
    )


@pytest.mark.asyncio
async def test_validate_inventory(order_service):
    # Arrange
    order_item = Mock(product_sku="ABC123", quantity=2)
    async_mock_response = AsyncMock()
    async_mock_response.__aenter__.return_value.status = 200
    async_mock_response.__aenter__.return_value.json.return_value = {
        "quantity": 3
    }

    # Patch the ClientSession's get method
    with patch(
        "aiohttp.ClientSession.get",
        return_value=async_mock_response,
    ) as mock_get:
        # Act
        result = await order_service.validate_inventory([order_item])
        # Assert
        assert result is True
        mock_get.assert_called_once()

    # Modify the mock response for insufficient quantity
    async_mock_response.__aenter__.return_value.json.return_value = {
        "quantity": 1
    }
    with patch(
        "aiohttp.ClientSession.get",
        return_value=async_mock_response,
    ) as mock_get:
        result = await order_service.validate_inventory([order_item])
        assert result is False
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_order_total(order_service):
    # Arrange
    order_item = Mock(product_sku="ABC123", quantity=2)
    order = Mock(spec=OrderEntity, order_items=[order_item])
    async_mock_response = AsyncMock()
    async_mock_response.__aenter__.return_value.status = 200
    async_mock_response.__aenter__.return_value.json.return_value = {
        "price": 25.00
    }

    with patch("aiohttp.ClientSession.get", return_value=async_mock_response):
        # Act
        total = await order_service.calculate_order_total(order)

        # Assert
        assert total == 50.00

        # Modify the mock response for a 404 error
    async_mock_response.__aenter__.return_value.status = 404
    with patch("aiohttp.ClientSession.get", return_value=async_mock_response):
        with pytest.raises(HTTPException) as excinfo:
            await order_service.calculate_order_total(order)
        assert excinfo.value.status_code == 404


def test_update_customer(order_service):
    # Arrange
    existing_customer = CustomerEntity(
        name="John Doe", email="john@example.com"
    )
    updated_customer = CustomerEntity(
        name="Jane Doe", email="jane@example.com"
    )
    order_service.customer_repository.find_by_email.return_value = (
        existing_customer
    )

    # Act
    result = order_service.update_customer(
        "jane@example.com", updated_customer
    )

    # Assert
    assert result == existing_customer
    order_service.customer_repository.save.assert_called_once_with(
        existing_customer
    )
    assert existing_customer.name == "Jane Doe"
    assert existing_customer.email == "jane@example.com"
    assert existing_customer.phone_number == updated_customer.phone_number


# Remaining tests


@pytest.mark.asyncio
async def test_create_order(order_service):
    # Arrange
    customer = Mock(spec=CustomerEntity, email="jane@example.com")
    order_item = Mock(spec=OrderItemEntity, product_sku="ABC123", quantity=2)
    order_service.customer_repository.find_by_email.return_value = None
    order_service.validate_inventory = AsyncMock(return_value=True)
    order_service.calculate_order_total = AsyncMock(return_value=50.00)

    # Act
    order = await order_service.create_order(customer, [order_item])

    # Assert
    order_service.customer_repository.save.assert_called_once_with(customer)
    order_service.order_repository.save.assert_called_once()
    order_service.inventory_publisher.publish_inventory_update.assert_called_once_with(
        "ABC123", "subtract", 2
    )
    assert order.total_amount == 50.00


@pytest.mark.asyncio
async def test_create_order_inventory_failure(order_service):
    # Arrange
    customer = Mock(spec=CustomerEntity, email="john@example.com")
    order_item = Mock(spec=OrderItemEntity, product_sku="ABC123", quantity=2)
    order_service.customer_repository.find_by_email.return_value = None
    order_service.validate_inventory = AsyncMock(return_value=False)

    # Act & Assert
    with pytest.raises(HTTPException):
        await order_service.create_order(customer, [order_item])


def test_get_order_by_id(order_service):
    # Arrange
    order = Mock(spec=OrderEntity, id=1)
    order_service.order_repository.find_by_id.return_value = order

    # Act
    result = order_service.get_order_by_id(1)

    # Assert
    assert result == order
    order_service.order_repository.find_by_id.assert_called_once_with(1)


def test_get_order_by_id_not_found(order_service):
    # Arrange
    order_service.order_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFound):
        order_service.get_order_by_id(1)


def test_update_order_status(order_service):
    # Arrange
    order = Mock(spec=OrderEntity, id=1, status=OrderStatus.PENDING)
    order_service.order_repository.find_by_id.return_value = order

    # Act
    result = order_service.update_order_status(1, OrderStatus.CONFIRMED)

    # Assert
    assert result == order
    order.update_status.assert_called_once_with(OrderStatus.CONFIRMED)
    order_service.order_repository.save.assert_called_once_with(order)


@pytest.mark.asyncio
async def test_confirm_order(order_service):
    # Arrange
    order = Mock(spec=OrderEntity, id=1, status=OrderStatus.PENDING)
    order_service.get_order_by_id = Mock(return_value=order)
    order_service.calculate_order_total = AsyncMock(return_value=50.00)
    order.update_status.side_effect = lambda status: setattr(
        order, "status", status
    )

    # Act
    result = await order_service.confirm_order(1)

    # Assert
    assert result == order
    order.update_status.assert_called_once_with(OrderStatus.CONFIRMED)
    order_service.order_repository.save.assert_called_once_with(order)
    order_service.order_update_publisher.publish_order_update.assert_called_once_with(
        order_id=1, amount=50.00, status="confirmed"
    )


def test_cancel_order(order_service):
    # Arrange
    order_item = Mock(spec=OrderItemEntity, product_sku="ABC123", quantity=2)
    order = Mock(
        spec=OrderEntity,
        id=1,
        status=OrderStatus.CONFIRMED,
        order_items=[order_item],
    )
    order_service.get_order_by_id = Mock(return_value=order)
    order.update_status.side_effect = lambda status: setattr(
        order, "status", status
    )

    # Act
    result = order_service.cancel_order(1)

    # Assert
    assert result == order
    order.update_status.assert_called_once_with(OrderStatus.CANCELED)
    order_service.inventory_publisher.publish_inventory_update.assert_called_once_with(
        "ABC123", "add", 2
    )
    order_service.order_update_publisher.publish_order_update.assert_called_once_with(
        order_id=1, amount=0.0, status="canceled"
    )


def test_create_customer(order_service):
    # Arrange
    customer = Mock(spec=CustomerEntity, email="john@example.com")
    order_service.customer_repository.find_by_email.return_value = None

    # Act
    result = order_service.create_customer(customer)

    # Assert
    assert result == customer
    order_service.customer_repository.save.assert_called_once_with(customer)


def test_create_customer_already_exists(order_service):
    # Arrange
    customer = Mock(spec=CustomerEntity, email="john@example.com")
    order_service.customer_repository.find_by_email.return_value = customer

    # Act & Assert
    with pytest.raises(EntityAlreadyExists):
        order_service.create_customer(customer)


def test_delete_customer(order_service):
    # Arrange
    customer = Mock(spec=CustomerEntity, email="john@example.com")
    order_service.customer_repository.find_by_email.return_value = customer

    # Act
    order_service.delete_customer("john@example.com")

    # Assert
    order_service.customer_repository.delete.assert_called_once_with(customer)


def test_delete_customer_not_found(order_service):
    # Arrange
    order_service.customer_repository.find_by_email.return_value = None

    # Act & Assert
    with pytest.raises(EntityNotFound):
        order_service.delete_customer("john@example.com")
