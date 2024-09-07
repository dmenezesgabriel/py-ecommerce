import math

import pytest
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import InvalidEntity


def test_order_item_entity_initialization():
    order_item = OrderItemEntity(
        product_sku="SKU123",
        quantity=10,
        name="Test Product",
        description="Test Description",
        price=99.99,
        id=1,
    )

    assert order_item.id == 1
    assert order_item.product_sku == "SKU123"
    assert order_item.quantity == 10
    assert order_item.name == "Test Product"
    assert order_item.description == "Test Description"
    assert math.isclose(order_item.price, 99.99, rel_tol=1e-9)


def test_order_item_entity_invalid_id():
    with pytest.raises(InvalidEntity):
        OrderItemEntity(
            product_sku="SKU123",
            quantity=10,
            id=-1,  # Invalid ID
        )


def test_order_item_entity_invalid_product_sku():
    with pytest.raises(InvalidEntity):
        OrderItemEntity(
            product_sku="",  # Invalid SKU
            quantity=10,
        )

    with pytest.raises(InvalidEntity):
        OrderItemEntity(
            product_sku=None,  # Invalid SKU (None)
            quantity=10,
        )


def test_order_item_entity_invalid_quantity():
    with pytest.raises(InvalidEntity):
        OrderItemEntity(
            product_sku="SKU123",
            quantity=-5,  # Invalid quantity
        )

    with pytest.raises(InvalidEntity):
        OrderItemEntity(
            product_sku="SKU123",
            quantity="invalid_quantity",  # Invalid quantity (not an integer)
        )


def test_order_item_entity_setters():
    order_item = OrderItemEntity(
        product_sku="SKU123",
        quantity=10,
        name="Test Product",
        description="Test Description",
        price=99.99,
    )

    order_item.id = 2
    assert order_item.id == 2

    order_item.product_sku = "SKU456"
    assert order_item.product_sku == "SKU456"

    order_item.quantity = 20
    assert order_item.quantity == 20

    order_item.name = "Updated Product"
    assert order_item.name == "Updated Product"

    order_item.description = "Updated Description"
    assert order_item.description == "Updated Description"

    order_item.price = 199.99
    assert math.isclose(order_item.price, 199.99, rel_tol=1e-9)


def test_order_item_entity_to_dict():
    order_item = OrderItemEntity(
        product_sku="SKU123",
        quantity=10,
        name="Test Product",
        description="Test Description",
        price=99.99,
        id=1,
    )

    expected_dict = {
        "id": 1,
        "product_sku": "SKU123",
        "quantity": 10,
        "name": "Test Product",
        "description": "Test Description",
        "price": 99.99,
    }

    assert order_item.to_dict() == expected_dict


def test_order_item_entity_invalid_id_setter():
    order_item = OrderItemEntity(
        product_sku="SKU123",
        quantity=10,
    )

    with pytest.raises(InvalidEntity):
        order_item.id = -1  # Invalid ID


def test_order_item_entity_invalid_product_sku_setter():
    order_item = OrderItemEntity(
        product_sku="SKU123",
        quantity=10,
    )

    with pytest.raises(InvalidEntity):
        order_item.product_sku = ""  # Invalid SKU


def test_order_item_entity_invalid_quantity_setter():
    order_item = OrderItemEntity(
        product_sku="SKU123",
        quantity=10,
    )

    with pytest.raises(InvalidEntity):
        order_item.quantity = -5  # Invalid quantity
