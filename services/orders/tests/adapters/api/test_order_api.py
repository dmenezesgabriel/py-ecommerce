from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from src.adapters.api import order_api
from src.application.dto.customer_dto import CustomerCreate
from src.application.dto.order_dto import (
    EstimatedTimeUpdate,
    OrderCreate,
    OrderStatusUpdate,
)
from src.application.dto.order_item_dto import OrderItemCreate
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import EntityNotFound, InvalidEntity


@pytest.fixture
def mock_order_service():
    return AsyncMock()


@pytest.fixture
def order_create_data():
    return OrderCreate(
        customer=CustomerCreate(
            name="John Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
        ),
        order_items=[
            OrderItemCreate(
                product_sku="SKU123",
                quantity=2,
            )
        ],
    )


@pytest.fixture
def order_entity(order_create_data):
    customer_entity = CustomerEntity(
        id=1,
        name=order_create_data.customer.name,
        email=order_create_data.customer.email,
        phone_number=order_create_data.customer.phone_number,
    )
    order_items_entities = [
        OrderItemEntity(
            id=1,
            product_sku="SKU123",
            quantity=2,
            name="Test",
            description="Test",
            price=99.99,
        )
    ]
    return OrderEntity(
        id=1, customer=customer_entity, order_items=order_items_entities
    )


@pytest.mark.asyncio
async def test_read_orders(mock_order_service, order_entity):
    mock_order_service.list_orders_paginated.return_value = (
        [order_entity],
        1,
        10,
        1,
        1,
    )
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.read_orders(service=mock_order_service)

    assert len(response.orders) == 1
    assert response.orders[0].customer.name == "John Doe"
    mock_order_service.list_orders_paginated.assert_called_once_with(1, 10)


@pytest.mark.asyncio
async def test_read_order(mock_order_service, order_entity):
    mock_order_service.get_order_by_id.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.read_order(
        order_id=1, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.get_order_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_read_order_not_found(mock_order_service):
    mock_order_service.get_order_by_id.side_effect = EntityNotFound(
        "Order not found"
    )

    with pytest.raises(HTTPException) as exc:
        await order_api.read_order(order_id=1, service=mock_order_service)

    assert exc.value.status_code == 404
    mock_order_service.get_order_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_update_order_not_found(mock_order_service, order_create_data):
    mock_order_service.update_order.side_effect = EntityNotFound(
        "Order not found"
    )

    with pytest.raises(HTTPException) as exc:
        await order_api.update_order(
            order_id=1, order=order_create_data, service=mock_order_service
        )

    assert exc.value.status_code == 404
    mock_order_service.update_order.assert_called_once_with(
        1,
        mock_order_service.update_order.call_args[0][1],
        mock_order_service.update_order.call_args[0][2],
    )


@pytest.mark.asyncio
async def test_update_order_status(mock_order_service, order_entity):
    mock_order_service.update_order_status.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    status_update = OrderStatusUpdate(status=OrderStatus.CONFIRMED)
    response = await order_api.update_order_status(
        order_id=1, status_update=status_update, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.update_order_status.assert_called_once_with(
        1, OrderStatus.CONFIRMED
    )


@pytest.mark.asyncio
async def test_confirm_order(mock_order_service, order_entity):
    mock_order_service.confirm_order.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.confirm_order(
        order_id=1, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.confirm_order.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_confirm_order_invalid(mock_order_service):
    mock_order_service.confirm_order.side_effect = InvalidEntity(
        "Invalid order"
    )

    with pytest.raises(HTTPException) as exc:
        await order_api.confirm_order(order_id=1, service=mock_order_service)

    assert exc.value.status_code == 400
    mock_order_service.confirm_order.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_cancel_order(mock_order_service, order_entity):
    mock_order_service.cancel_order.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.cancel_order(
        order_id=1, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.cancel_order.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_order(mock_order_service):
    response = await order_api.delete_order(
        order_id=1, service=mock_order_service
    )

    assert response == {"message": "Order deleted successfully"}
    mock_order_service.delete_order.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_set_estimated_time(mock_order_service, order_entity):
    mock_order_service.set_estimated_time.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    estimated_time_update = EstimatedTimeUpdate(
        estimated_time="2024-09-01T12:00:00Z"
    )
    response = await order_api.set_estimated_time(
        order_id=1,
        estimated_time_update=estimated_time_update,
        service=mock_order_service,
    )

    assert response.customer.name == "John Doe"
    mock_order_service.set_estimated_time.assert_called_once_with(
        1, "2024-09-01T12:00:00Z"
    )


@pytest.mark.asyncio
async def test_update_order_to_received(mock_order_service, order_entity):
    mock_order_service.update_order_status.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.update_order_to_received(
        order_id=1, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.update_order_status.assert_called_once_with(
        1, OrderStatus.RECEIVED
    )


@pytest.mark.asyncio
async def test_update_order_to_preparing(mock_order_service, order_entity):
    mock_order_service.update_order_status.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.update_order_to_preparing(
        order_id=1, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.update_order_status.assert_called_once_with(
        1, OrderStatus.PREPARING
    )


@pytest.mark.asyncio
async def test_update_order_to_ready(mock_order_service, order_entity):
    mock_order_service.update_order_status.return_value = order_entity
    mock_order_service.calculate_order_total.return_value = 100.0

    response = await order_api.update_order_to_ready(
        order_id=1, service=mock_order_service
    )

    assert response.customer.name == "John Doe"
    mock_order_service.update_order_status.assert_called_once_with(
        1, OrderStatus.READY
    )
