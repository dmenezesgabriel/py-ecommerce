from unittest.mock import patch

import pytest
from pydantic import ValidationError
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse


def test_customer_create_valid():
    customer_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+123456789",
    }
    customer = CustomerCreate(**customer_data)

    assert customer.name == customer_data["name"]
    assert customer.email == customer_data["email"]
    assert customer.phone_number == customer_data["phone_number"]


def test_customer_create_optional_phone_number():
    customer_data = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
    }
    customer = CustomerCreate(**customer_data)

    assert customer.name == customer_data["name"]
    assert customer.email == customer_data["email"]
    assert customer.phone_number is None


def test_customer_response_valid():
    customer_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+123456789",
    }
    customer = CustomerResponse(**customer_data)

    assert customer.id == customer_data["id"]
    assert customer.name == customer_data["name"]
    assert customer.email == customer_data["email"]
    assert customer.phone_number == customer_data["phone_number"]


def test_customer_response_optional_phone_number():
    customer_data = {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone_number": None,
    }
    customer = CustomerResponse(**customer_data)

    assert customer.id == customer_data["id"]
    assert customer.name == customer_data["name"]
    assert customer.email == customer_data["email"]
    assert customer.phone_number is None


def test_customer_response_invalid_id():
    customer_data = {
        "id": "invalid_id",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+123456789",
    }
    with pytest.raises(ValidationError):
        CustomerResponse(**customer_data)


def test_customer_create_json_schema_extra():
    with patch("pydantic.BaseModel.model_config") as mock_config:
        mock_config.get.return_value = CustomerCreate.model_config
        examples = CustomerCreate.model_config["json_schema_extra"]["examples"]

        assert len(examples) == 2
        assert examples[0]["name"] == "John Doe"
        assert examples[1]["name"] == "Jane Smith"


def test_customer_response_json_schema_extra():
    with patch("pydantic.BaseModel.model_config") as mock_config:
        mock_config.get.return_value = CustomerResponse.model_config
        examples = CustomerResponse.model_config["json_schema_extra"][
            "examples"
        ]

        assert len(examples) == 2
        assert examples[0]["id"] == 1
        assert examples[1]["id"] == 2
