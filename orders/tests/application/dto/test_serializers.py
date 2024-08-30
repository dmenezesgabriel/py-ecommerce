from unittest.mock import MagicMock

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
    customer = MagicMock(spec=CustomerEntity)
    customer.id = 1
    customer.name = "John Doe"
    customer.email = "john.doe@example.com"
    customer.phone_number = "+123456789"

    serialized_customer = serialize_customer(customer)

    assert isinstance(serialized_customer, CustomerResponse)
    assert serialized_customer.id == 1
    assert serialized_customer.name == "John Doe"
    assert serialized_customer.email == "john.doe@example.com"
    assert serialized_customer.phone_number == "+123456789"


def test_serialize_order_item():
    order_item = MagicMock(spec=OrderItemEntity)
    order_item.product_sku = "ABC123"
    order_item.quantity = 2
    order_item.name = "Product Name"
    order_item.description = "Product Description"
    order_item.price = 10.00

    serialized_order_item = serialize_order_item(order_item)

    assert isinstance(serialized_order_item, OrderItemResponse)
    assert serialized_order_item.product_sku == "ABC123"
    assert serialized_order_item.quantity == 2
    assert serialized_order_item.name == "Product Name"
    assert serialized_order_item.description == "Product Description"
    assert serialized_order_item.price == 10.00


def test_serialize_order():
    customer = MagicMock(spec=CustomerEntity)
    customer.id = 1
    customer.name = "John Doe"
    customer.email = "john.doe@example.com"
    customer.phone_number = "+123456789"

    order_item1 = MagicMock(spec=OrderItemEntity)
    order_item1.product_sku = "ABC123"
    order_item1.quantity = 2
    order_item1.name = "Product Name"
    order_item1.description = "Product Description"
    order_item1.price = 10.00

    order_item2 = MagicMock(spec=OrderItemEntity)
    order_item2.product_sku = "XYZ456"
    order_item2.quantity = 1
    order_item2.name = "Product Name 2"
    order_item2.description = "Product Description 2"
    order_item2.price = 20.00

    order = MagicMock(spec=OrderEntity)
    order.id = 1
    order.order_number = "ORD123"
    order.customer = customer
    order.order_items = [order_item1, order_item2]
    order.status = OrderStatus.CONFIRMED
    order.estimated_time = "02:30"

    serialized_order = serialize_order(order, total_amount=40.00)

    assert isinstance(serialized_order, OrderResponse)
    assert serialized_order.id == 1
    assert serialized_order.order_number == "ORD123"
    assert serialized_order.customer.id == 1
    assert len(serialized_order.order_items) == 2
    assert serialized_order.order_items[0].product_sku == "ABC123"
    assert serialized_order.status == OrderStatus.CONFIRMED
    assert serialized_order.total_amount == 40.00
    assert serialized_order.estimated_time == "02:30"


def test_serialize_order_empty_items():
    customer = MagicMock(spec=CustomerEntity)
    customer.id = 1
    customer.name = "John Doe"
    customer.email = "john.doe@example.com"
    customer.phone_number = "+123456789"

    order = MagicMock(spec=OrderEntity)
    order.id = 1
    order.order_number = "ORD123"
    order.customer = customer
    order.order_items = []
    order.status = OrderStatus.PENDING
    order.estimated_time = None

    serialized_order = serialize_order(order, total_amount=0.00)

    assert isinstance(serialized_order, OrderResponse)
    assert serialized_order.id == 1
    assert serialized_order.order_number == "ORD123"
    assert serialized_order.customer.id == 1
    assert len(serialized_order.order_items) == 0
    assert serialized_order.status == OrderStatus.PENDING
    assert serialized_order.total_amount == 0.00
    assert serialized_order.estimated_time is None
