import unittest
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session
from src.domain.entities.customer_entity import CustomerEntity
from src.infrastructure.persistence.models import CustomerModel
from src.infrastructure.persistence.sqlalchemy_customer_repository import (
    SQLAlchemyCustomerRepository,
)


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@pytest.fixture
def customer_repository(mock_session):
    return SQLAlchemyCustomerRepository(db=mock_session)


def test_save_new_customer(customer_repository, mock_session):
    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    mock_db_customer = MagicMock(spec=CustomerModel)
    mock_db_customer.id = 1  # Explicitly setting the ID to an integer
    mock_session.query(CustomerModel).filter().first.return_value = None
    mock_session.add.return_value = None
    mock_session.refresh.return_value = None
    mock_session.refresh.side_effect = lambda x: setattr(
        x, "id", mock_db_customer.id
    )

    customer_repository.save(customer)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_save_existing_customer(customer_repository, mock_session):
    db_customer = MagicMock(spec=CustomerModel)
    db_customer.id = 1  # Explicitly setting the ID to an integer
    mock_session.query(CustomerModel).filter().first.return_value = db_customer

    customer = CustomerEntity(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    customer_repository.save(customer)

    assert db_customer.name == "John Doe"
    assert db_customer.email == "john.doe@example.com"
    assert db_customer.phone_number == "+123456789"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_find_by_email_existing_customer(customer_repository, mock_session):
    # Mocking an existing customer in the database
    db_customer = MagicMock(spec=CustomerModel)
    db_customer.id = 1
    db_customer.name = "John Doe"
    db_customer.email = "john.doe@example.com"
    db_customer.phone_number = "+123456789"
    db_customer.deleted = 0
    mock_session.query(CustomerModel).filter().first.return_value = db_customer

    customer = customer_repository.find_by_email("john.doe@example.com")

    assert customer is not None
    assert customer.id == 1
    assert customer.name == "John Doe"
    assert customer.email == "john.doe@example.com"
    assert customer.phone_number == "+123456789"
    mock_session.query(CustomerModel).filter().first.assert_called_once()


def test_find_by_email_non_existing_customer(
    customer_repository, mock_session
):
    # Mocking a non-existing customer
    mock_session.query(CustomerModel).filter().first.return_value = None

    customer = customer_repository.find_by_email("non.existing@example.com")

    assert customer is None
    mock_session.query(CustomerModel).filter().first.assert_called_once()


def test_list_all_customers(customer_repository, mock_session):
    # Mocking a list of customers in the database
    db_customer1 = MagicMock(spec=CustomerModel)
    db_customer1.id = 1
    db_customer1.name = "John Doe"
    db_customer1.email = "john.doe@example.com"
    db_customer1.phone_number = "+123456789"
    db_customer1.deleted = 0

    db_customer2 = MagicMock(spec=CustomerModel)
    db_customer2.id = 2
    db_customer2.name = "Jane Doe"
    db_customer2.email = "jane.doe@example.com"
    db_customer2.phone_number = "+987654321"
    db_customer2.deleted = 0

    mock_session.query(CustomerModel).filter().all.return_value = [
        db_customer1,
        db_customer2,
    ]

    customers = customer_repository.list_all()

    assert len(customers) == 2
    assert customers[0].id == 1
    assert customers[0].name == "John Doe"
    assert customers[0].email == "john.doe@example.com"
    assert customers[0].phone_number == "+123456789"
    assert customers[1].id == 2
    assert customers[1].name == "Jane Doe"
    assert customers[1].email == "jane.doe@example.com"
    assert customers[1].phone_number == "+987654321"
    mock_session.query(CustomerModel).filter().all.assert_called_once()


def test_delete_customer(customer_repository, mock_session):
    # Mocking an existing customer to delete
    db_customer = MagicMock(spec=CustomerModel)
    db_customer.id = 1
    mock_session.query(CustomerModel).filter().first.return_value = db_customer

    customer = CustomerEntity(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    customer_repository.delete(customer)

    assert db_customer.name == f"deleted_user_{db_customer.id}"
    assert db_customer.email == f"deleted_email_{db_customer.id}@example.com"
    assert db_customer.phone_number == f"deleted_phone_number_{db_customer.id}"
    assert db_customer.deleted == 1
    mock_session.commit.assert_called_once()
