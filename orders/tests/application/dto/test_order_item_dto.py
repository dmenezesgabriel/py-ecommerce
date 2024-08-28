from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError
from src.application.dto.order_item_dto import (
    OrderItemCreate,
    OrderItemResponse,
)

# Arrange, Act, Assert methodology is followed in each test


def test_order_item_create_valid_data():
    # Arrange
    valid_data = {"product_sku": "123", "quantity": 2}

    # Act
    order_item = OrderItemCreate(**valid_data)

    # Assert
    assert order_item.product_sku == "123"
    assert order_item.quantity == 2


def test_order_item_create_invalid_quantity():
    # Arrange
    invalid_data = {
        "product_sku": "123",
        "quantity": "two",  # Invalid data type
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        OrderItemCreate(**invalid_data)


def test_order_item_response_valid_data():
    # Arrange
    valid_data = {"product_sku": "ABC123", "quantity": 2}

    # Act
    order_item = OrderItemResponse(**valid_data)

    # Assert
    assert order_item.product_sku == "ABC123"
    assert order_item.quantity == 2


def test_order_item_response_from_attributes():
    # Arrange
    attributes = Mock(product_sku="XYZ456", quantity=1)

    # Act
    order_item = OrderItemResponse.model_validate(attributes)

    # Assert
    assert order_item.product_sku == "XYZ456"
    assert order_item.quantity == 1


@patch(
    "src.application.dto.order_item_dto.OrderItemCreate.model_config",
    new_callable=Mock,
)
def test_order_item_create_model_config(mock_model_config):
    # Arrange
    mock_model_config.json_schema_extra = {
        "examples": [{"product_sku": "123", "quantity": 2}]
    }

    # Act
    config = OrderItemCreate.model_config

    # Assert
    assert config.json_schema_extra["examples"][0]["product_sku"] == "123"
    assert config.json_schema_extra["examples"][0]["quantity"] == 2
    assert mock_model_config.json_schema_extra is not None


@patch(
    "src.application.dto.order_item_dto.OrderItemResponse.model_config",
    new_callable=Mock,
)
def test_order_item_response_model_config(mock_model_config):
    # Arrange
    mock_model_config.from_attributes = True

    # Act
    config = OrderItemResponse.model_config

    # Assert
    assert config.from_attributes is True
    assert mock_model_config.from_attributes is not None
