from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from src.domain.entities.order_entity import OrderStatus
from src.infrastructure.persistence.models import (
    CustomerModel,
    OrderItemModel,
    OrderModel,
)


@pytest.fixture
def mock_base():
    with patch(
        "src.infrastructure.persistence.models.Base", autospec=True
    ) as mock_base:
        yield mock_base


@patch.object(
    CustomerModel, "deleted", new_callable=PropertyMock, return_value=0
)
def test_customer_model_initialization(mock_deleted, mock_base):
    customer = CustomerModel(
        name="John Doe", email="john.doe@example.com", phone_number="123456789"
    )

    assert customer.name == "John Doe"
    assert customer.email == "john.doe@example.com"
    assert customer.phone_number == "123456789"
    assert customer.deleted == 0
    mock_deleted.assert_called_once()


@patch("uuid.uuid4", return_value="mocked-uuid")
@patch.object(
    OrderModel,
    "order_number",
    new_callable=PropertyMock,
    return_value="mocked-uuid",
)
def test_order_model_initialization(mock_order_number, mock_uuid4, mock_base):
    order = OrderModel(
        customer_id=1,
        status=OrderStatus.PENDING,
        estimated_time="2024-09-01 12:00:00",
    )

    assert order.customer_id == 1
    assert order.status == OrderStatus.PENDING
    assert order.estimated_time == "2024-09-01 12:00:00"
    assert order.order_number == "mocked-uuid"
    mock_order_number.assert_called_once()


def test_order_item_model_initialization(mock_base):
    order_item = OrderItemModel(order_id=1, product_sku="SKU123", quantity=2)

    assert order_item.order_id == 1
    assert order_item.product_sku == "SKU123"
    assert order_item.quantity == 2


def test_relationships(mock_base):
    with patch.object(
        CustomerModel, "orders", new_callable=MagicMock
    ) as mock_orders:
        customer = CustomerModel(name="John Doe", email="john.doe@example.com")
        assert customer.orders == mock_orders

    with patch.object(
        OrderModel, "customer", new_callable=MagicMock
    ) as mock_customer:
        order = OrderModel(customer_id=1)
        assert order.customer == mock_customer

    with patch.object(
        OrderModel, "order_items", new_callable=MagicMock
    ) as mock_order_items:
        order = OrderModel(customer_id=1)
        assert order.order_items == mock_order_items

    with patch.object(
        OrderItemModel, "order", new_callable=MagicMock
    ) as mock_order:
        order_item = OrderItemModel(order_id=1)
        assert order_item.order == mock_order
