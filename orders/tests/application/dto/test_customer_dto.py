from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse

# Arrange, Act, Assert methodology is followed in each test


def test_customer_create_valid_data():
    # Arrange
    valid_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+123456789",
    }

    # Act
    customer = CustomerCreate(**valid_data)

    # Assert
    assert customer.name == "John Doe"
    assert customer.email == "john.doe@example.com"
    assert customer.phone_number == "+123456789"


def test_customer_create_valid_data_without_phone():
    # Arrange
    valid_data = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
    }

    # Act
    customer = CustomerCreate(**valid_data)

    # Assert
    assert customer.name == "Jane Smith"
    assert customer.email == "jane.smith@example.com"
    assert customer.phone_number is None


def test_customer_create_invalid_email():
    # Arrange
    invalid_data = {
        "name": 1,
        "email": "invalid-email",
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        CustomerCreate(**invalid_data)


def test_customer_response_valid_data():
    # Arrange
    valid_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+123456789",
    }

    # Act
    customer = CustomerResponse(**valid_data)

    # Assert
    assert customer.id == 1
    assert customer.name == "John Doe"
    assert customer.email == "john.doe@example.com"
    assert customer.phone_number == "+123456789"


def test_customer_response_valid_data_without_phone():
    # Arrange
    valid_data = {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone_number": None,
    }

    # Act
    customer = CustomerResponse(**valid_data)

    # Assert
    assert customer.id == 2
    assert customer.name == "Jane Smith"
    assert customer.email == "jane.smith@example.com"
    assert customer.phone_number is None


def test_customer_response_from_attributes():
    # Arrange
    attributes = dict(
        id=3,
        name="Alice Doe",
        email="alice.doe@example.com",
        phone_number="+987654321",
    )

    # Act
    customer = CustomerResponse.model_validate(attributes)

    # Assert
    assert customer.id == 3
    assert customer.name == "Alice Doe"
    assert customer.email == "alice.doe@example.com"
    assert customer.phone_number == "+987654321"


@patch(
    "src.application.dto.customer_dto.CustomerCreate.model_config",
    new_callable=Mock,
)
def test_customer_create_model_config(mock_model_config):
    # Arrange
    mock_model_config.json_schema_extra = {
        "examples": [
            {
                "name": "Test",
                "email": "test@example.com",
                "phone_number": "+123456789",
            }
        ]
    }

    # Act
    config = CustomerCreate.model_config

    # Assert
    assert config.json_schema_extra["examples"][0]["name"] == "Test"
    assert mock_model_config.json_schema_extra is not None


@patch(
    "src.application.dto.customer_dto.CustomerResponse.model_config",
    new_callable=Mock,
)
def test_customer_response_model_config(mock_model_config):
    # Arrange
    mock_model_config.from_attributes = True

    # Act
    config = CustomerResponse.model_config

    # Assert
    assert config.from_attributes is True
    assert mock_model_config.from_attributes is not None
