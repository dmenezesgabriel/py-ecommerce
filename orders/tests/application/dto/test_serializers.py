from unittest.mock import Mock

import pytest
from src.application.dto.customer_dto import CustomerResponse
from src.application.dto.order_dto import OrderResponse
from src.application.dto.order_item_dto import OrderItemResponse
from src.application.dto.serializers import (
    serialize_customer,
    serialize_order,
    serialize_order_item,
)
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity


def test_serialize_customer():
    # Arrange
    customer_entity = CustomerEntity(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    # Act
    customer_response = serialize_customer(customer_entity)

    # Assert
    assert isinstance(customer_response, CustomerResponse)
    assert customer_response.id == 1
    assert customer_response.name == "John Doe"
    assert customer_response.email == "john.doe@example.com"
    assert customer_response.phone_number == "+123456789"


def test_serialize_order_item():
    # Arrange
    order_item_entity = Mock(
        product_sku="ABC123",
        quantity=2,
    )

    # Act
    order_item_response = serialize_order_item(order_item_entity)

    # Assert
    assert isinstance(order_item_response, OrderItemResponse)
    assert order_item_response.product_sku == "ABC123"
    assert order_item_response.quantity == 2


def test_serialize_order():
    # Arrange
    customer_entity = CustomerEntity(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    order_item_entity1 = OrderItemEntity(
        product_sku="ABC123",
        quantity=2,
    )
    order_item_entity2 = OrderItemEntity(
        product_sku="XYZ456",
        quantity=1,
    )
    order_entity = OrderEntity(
        id=1,
        order_number="ORD123",
        customer=customer_entity,
        order_items=[order_item_entity1, order_item_entity2],
        status=OrderStatus.CONFIRMED,
    )

    # Act
    order_response = serialize_order(order_entity, total_amount=30.00)

    # Assert
    assert isinstance(order_response, OrderResponse)
    assert order_response.id == 1
    assert order_response.order_number == "ORD123"
    assert order_response.customer.name == "John Doe"
    assert len(order_response.order_items) == 2
    assert order_response.order_items[0].product_sku == "ABC123"
    assert order_response.status == OrderStatus.CONFIRMED
    assert order_response.total_amount == 30.00
