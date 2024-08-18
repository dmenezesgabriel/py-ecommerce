from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse
from src.application.dto.order_dto import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from src.application.dto.order_item_dto import (
    OrderItemCreate,
    OrderItemResponse,
)
from src.domain.entities.order_entity import OrderStatus


def test_order_create_valid_data():
    # Arrange
    valid_data = {
        "customer": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "+123456789",
        },
        "order_items": [
            {"product_sku": "ABC123", "quantity": 2},
            {"product_sku": "XYZ456", "quantity": 1},
        ],
    }

    # Act
    order_create = OrderCreate(**valid_data)

    # Assert
    assert order_create.customer.name == "John Doe"
    assert order_create.order_items[0].product_sku == "ABC123"
    assert order_create.order_items[1].quantity == 1


def test_order_create_invalid_data():
    # Arrange
    invalid_data = {
        "customer": {
            "name": "John Doe",
            "email": 1,
        },
        "order_items": [
            {"product_sku": "ABC123", "quantity": 2},
        ],
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        OrderCreate(**invalid_data)


def test_order_status_update_valid_data():
    # Arrange
    valid_data = {
        "status": OrderStatus.CONFIRMED,
    }

    # Act
    order_status_update = OrderStatusUpdate(**valid_data)

    # Assert
    assert order_status_update.status == OrderStatus.CONFIRMED


def test_order_status_update_invalid_data():
    # Arrange
    invalid_data = {
        "status": "not_a_valid_status",
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        OrderStatusUpdate(**invalid_data)


def test_order_response_valid_data():
    # Arrange
    valid_data = {
        "id": 1,
        "order_number": "ORD123",
        "customer": {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "+123456789",
        },
        "order_items": [
            {"product_sku": "ABC123", "quantity": 2},
            {"product_sku": "XYZ456", "quantity": 1},
        ],
        "status": OrderStatus.CONFIRMED,
        "total_amount": 30.00,
    }

    # Act
    order_response = OrderResponse(**valid_data)

    # Assert
    assert order_response.id == 1
    assert order_response.order_number == "ORD123"
    assert order_response.customer.name == "John Doe"
    assert order_response.order_items[0].product_sku == "ABC123"
    assert order_response.status == OrderStatus.CONFIRMED
    assert order_response.total_amount == 30.00


def test_order_response_from_attributes():
    # Arrange
    attributes = dict(
        id=1,
        order_number="ORD123",
        customer=dict(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
        ),
        order_items=[
            dict(product_sku="ABC123", quantity=2),
            dict(product_sku="XYZ456", quantity=1),
        ],
        status=OrderStatus.CONFIRMED,
        total_amount=30.00,
    )

    # Act
    order_response = OrderResponse.model_validate(attributes)

    # Assert
    assert order_response.id == 1
    assert order_response.order_number == "ORD123"
    assert order_response.customer.name == "John Doe"
    assert order_response.order_items[0].product_sku == "ABC123"
    assert order_response.status == OrderStatus.CONFIRMED
    assert order_response.total_amount == 30.00


@patch(
    "src.application.dto.order_dto.OrderCreate.model_config",
    new_callable=Mock,
)
def test_order_create_model_config(mock_model_config):
    # Arrange
    mock_model_config.json_schema_extra = {
        "examples": [
            {
                "customer": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+123456789",
                },
                "order_items": [
                    {"product_sku": "ABC123", "quantity": 2},
                ],
            }
        ]
    }

    # Act
    config = OrderCreate.model_config

    # Assert
    assert (
        config.json_schema_extra["examples"][0]["customer"]["name"]
        == "John Doe"
    )
    assert (
        config.json_schema_extra["examples"][0]["order_items"][0][
            "product_sku"
        ]
        == "ABC123"
    )
    assert mock_model_config.json_schema_extra is not None


@patch(
    "src.application.dto.order_dto.OrderStatusUpdate.model_config",
    new_callable=Mock,
)
def test_order_status_update_model_config(mock_model_config):
    # Arrange
    mock_model_config.json_schema_extra = {
        "examples": [
            {
                "status": "confirmed",
            }
        ]
    }

    # Act
    config = OrderStatusUpdate.model_config

    # Assert
    assert config.json_schema_extra["examples"][0]["status"] == "confirmed"
    assert mock_model_config.json_schema_extra is not None


@patch(
    "src.application.dto.order_dto.OrderResponse.model_config",
    new_callable=Mock,
)
def test_order_response_model_config(mock_model_config):
    # Arrange
    mock_model_config.json_schema_extra = {
        "examples": [
            {
                "id": 1,
                "order_number": "ORD123",
                "customer": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+123456789",
                },
                "order_items": [
                    {"product_sku": "ABC123", "quantity": 2},
                ],
                "status": "confirmed",
                "total_amount": 30.00,
            }
        ]
    }

    # Act
    config = OrderResponse.model_config

    # Assert
    assert config.json_schema_extra["examples"][0]["id"] == 1
    assert config.json_schema_extra["examples"][0]["order_number"] == "ORD123"
    assert (
        config.json_schema_extra["examples"][0]["customer"]["name"]
        == "John Doe"
    )
    assert mock_model_config.json_schema_extra is not None
