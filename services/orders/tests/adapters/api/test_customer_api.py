from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from src.adapters.api.customer_api import (
    create_customer,
    delete_customer,
    read_customer,
    read_customers,
    update_customer,
)
from src.application.dto.customer_dto import CustomerCreate
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.exceptions import EntityAlreadyExists, EntityNotFound


@pytest.fixture
def mock_order_service():
    return MagicMock()


@pytest.mark.asyncio
async def test_read_customers(mock_order_service):
    mock_order_service.get_all_customers.return_value = [
        CustomerEntity(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
        )
    ]

    result = await read_customers(service=mock_order_service)

    assert len(result) == 1
    assert result[0].name == "John Doe"
    mock_order_service.get_all_customers.assert_called_once()


@pytest.mark.asyncio
async def test_read_customer_found(mock_order_service):
    mock_order_service.get_customer_by_email.return_value = CustomerEntity(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    result = await read_customer(
        "john.doe@example.com", service=mock_order_service
    )

    assert result.name == "John Doe"
    mock_order_service.get_customer_by_email.assert_called_once_with(
        "john.doe@example.com"
    )


@pytest.mark.asyncio
async def test_read_customer_not_found(mock_order_service):
    mock_order_service.get_customer_by_email.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await read_customer("john.doe@example.com", service=mock_order_service)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Customer not found"
    mock_order_service.get_customer_by_email.assert_called_once_with(
        "john.doe@example.com"
    )


@pytest.mark.asyncio
async def test_create_customer_success(mock_order_service):
    customer_data = CustomerCreate(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    customer_entity = CustomerEntity(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    mock_order_service.create_customer.return_value = customer_entity

    result = await create_customer(customer_data, service=mock_order_service)

    assert result.name == "John Doe"
    mock_order_service.create_customer.assert_called_once()


@pytest.mark.asyncio
async def test_create_customer_already_exists(mock_order_service):
    customer_data = CustomerCreate(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    mock_order_service.create_customer.side_effect = EntityAlreadyExists(
        "Customer already exists"
    )

    with pytest.raises(HTTPException) as excinfo:
        await create_customer(customer_data, service=mock_order_service)

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Customer already exists"
    mock_order_service.create_customer.assert_called_once()


@pytest.mark.asyncio
async def test_update_customer_success(mock_order_service):
    customer_data = CustomerCreate(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    customer_entity = CustomerEntity(
        id=1,
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )

    mock_order_service.update_customer.return_value = customer_entity

    result = await update_customer(
        "john.doe@example.com", customer_data, service=mock_order_service
    )

    assert result.name == "John Doe"

    # Instead of comparing the objects directly, compare the attributes
    mock_order_service.update_customer.assert_called_once()
    args, kwargs = mock_order_service.update_customer.call_args
    assert args[0] == "john.doe@example.com"
    assert args[1].name == customer_entity.name
    assert args[1].email == customer_entity.email
    assert args[1].phone_number == customer_entity.phone_number


@pytest.mark.asyncio
async def test_update_customer_not_found(mock_order_service):
    customer_data = CustomerCreate(
        name="John Doe",
        email="john.doe@example.com",
        phone_number="+123456789",
    )
    mock_order_service.update_customer.side_effect = EntityNotFound(
        "Customer not found"
    )

    with pytest.raises(HTTPException) as excinfo:
        await update_customer(
            "john.doe@example.com", customer_data, service=mock_order_service
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Customer not found"
    mock_order_service.update_customer.assert_called_once()


@pytest.mark.asyncio
async def test_delete_customer_success(mock_order_service):
    result = await delete_customer(
        "john.doe@example.com", service=mock_order_service
    )

    assert result["message"] == "Customer deleted successfully"
    mock_order_service.delete_customer.assert_called_once_with(
        "john.doe@example.com"
    )


@pytest.mark.asyncio
async def test_delete_customer_not_found(mock_order_service):
    mock_order_service.delete_customer.side_effect = EntityNotFound(
        "Customer not found"
    )

    with pytest.raises(HTTPException) as excinfo:
        await delete_customer(
            "john.doe@example.com", service=mock_order_service
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Customer not found"
    mock_order_service.delete_customer.assert_called_once_with(
        "john.doe@example.com"
    )
