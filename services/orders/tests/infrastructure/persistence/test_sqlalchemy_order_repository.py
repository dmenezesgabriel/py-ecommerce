import unittest
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity
from src.domain.entities.order_item_entity import OrderItemEntity
from src.infrastructure.persistence.models import (
    CustomerModel,
    OrderItemModel,
    OrderModel,
)
from src.infrastructure.persistence.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository,
)


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def order_repository(mock_session):
    return SQLAlchemyOrderRepository(db=mock_session)


def test_save_new_order(order_repository, mock_session):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    order = OrderEntity(
        customer=customer,
        order_number="ORD123",
        status="PENDING",
        estimated_time="2024-09-01 12:00:00",
        order_items=[],
    )

    mock_customer_model = MagicMock(spec=CustomerModel)
    mock_customer_model.id = 1
    mock_session.query(CustomerModel).filter().first.return_value = None
    mock_session.add.return_value = None
    mock_session.refresh.side_effect = lambda x: setattr(
        x, "id", mock_customer_model.id
    )

    mock_order_model = MagicMock(spec=OrderModel)
    mock_order_model.id = 1
    mock_session.query(OrderModel).filter().first.return_value = None

    order_repository.save(order)

    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()


def test_save_existing_order(order_repository, mock_session):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    order = OrderEntity(
        id=1,
        customer=customer,
        order_number="ORD123",
        status="PENDING",
        estimated_time="2024-09-01 12:00:00",
        order_items=[],
    )

    mock_customer_model = MagicMock(spec=CustomerModel)
    mock_customer_model.id = 1
    mock_session.query(CustomerModel).filter().first.return_value = (
        mock_customer_model
    )

    mock_order_model = MagicMock(spec=OrderModel)
    mock_order_model.id = 1
    mock_session.query(OrderModel).filter().first.return_value = (
        mock_order_model
    )

    order_repository.save(order)

    assert mock_order_model.status == order.status
    assert mock_order_model.estimated_time == order.estimated_time
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()


def test_find_by_id_non_existing_order(order_repository, mock_session):
    mock_session.query(OrderModel).filter().first.return_value = None

    order = order_repository.find_by_id(1)

    assert order is None


def test_find_by_order_number_non_existing_order(
    order_repository, mock_session
):
    mock_session.query(OrderModel).filter().first.return_value = None

    order = order_repository.find_by_order_number("ORD123")

    assert order is None


def test_delete_existing_order(order_repository, mock_session):
    mock_order_model = MagicMock(spec=OrderModel)
    mock_order_model.id = 1
    mock_session.query(OrderModel).filter().first.return_value = (
        mock_order_model
    )

    mock_customer = MagicMock(spec=CustomerEntity)
    mock_customer.id = 1

    order = OrderEntity(
        id=1,
        customer=mock_customer,
        order_number="ORD123",
        status="PENDING",
        estimated_time="2024-09-01 12:00:00",
        order_items=[],
    )

    order_repository.delete(order)

    mock_session.delete.assert_called_with(mock_order_model)
    mock_session.commit.assert_called()
