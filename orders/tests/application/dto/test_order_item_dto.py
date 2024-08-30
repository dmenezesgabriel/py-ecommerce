import pytest
from pydantic import ValidationError
from src.application.dto.order_item_dto import (
    OrderItemCreate,
    OrderItemResponse,
)


def test_order_item_create_valid():
    order_item_data = {"product_sku": "ABC123", "quantity": 2}
    order_item = OrderItemCreate(**order_item_data)

    assert order_item.product_sku == "ABC123"
    assert order_item.quantity == 2


def test_order_item_create_missing_field():
    order_item_data = {"quantity": 2}

    with pytest.raises(ValidationError):
        OrderItemCreate(**order_item_data)


def test_order_item_response_valid():
    order_item_data = {
        "product_sku": "ABC123",
        "quantity": 2,
        "name": "Product Name",
        "description": "Product Description",
        "price": 10.00,
    }
    order_item = OrderItemResponse(**order_item_data)

    assert order_item.product_sku == "ABC123"
    assert order_item.quantity == 2
    assert order_item.name == "Product Name"
    assert order_item.description == "Product Description"
    assert order_item.price == 10.00


def test_order_item_response_missing_field():
    order_item_data = {
        "product_sku": "ABC123",
        "quantity": 2,
        "name": "Product Name",
        # Missing description and price
    }

    with pytest.raises(ValidationError):
        OrderItemResponse(**order_item_data)


def test_order_item_response_invalid_price():
    order_item_data = {
        "product_sku": "ABC123",
        "quantity": 2,
        "name": "Product Name",
        "description": "Product Description",
        "price": "invalid_price",  # Invalid price
    }

    with pytest.raises(ValidationError):
        OrderItemResponse(**order_item_data)
