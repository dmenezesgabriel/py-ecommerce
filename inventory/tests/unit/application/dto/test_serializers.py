from unittest.mock import Mock

import pytest
from src.application.dto.category_dto import CategoryResponse
from src.application.dto.product_dto import ProductResponse
from src.application.dto.serializers import (
    serialize_category,
    serialize_product,
)
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.product_entity import ProductEntity


class TestSerializeFunctions:

    def test_serialize_product(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        category.name = "Food"

        price = Mock()
        price.amount = 1.50

        inventory = Mock()
        inventory.quantity = 100

        product = Mock(spec=ProductEntity)
        product.sku = "123"
        product.name = "Potato Sauce"
        product.category = category
        product.price = price
        product.inventory = inventory

        # Act
        result = serialize_product(product)

        # Assert
        assert isinstance(result, ProductResponse)
        assert result.sku == "123"
        assert result.name == "Potato Sauce"
        assert result.category_name == "Food"
        assert result.price == 1.50
        assert result.quantity == 100

    def test_serialize_category(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        category.id = 1
        category.name = "Food"

        # Act
        result = serialize_category(category)

        # Assert
        assert isinstance(result, CategoryResponse)
        assert result.id == 1
        assert result.name == "Food"


if __name__ == "__main__":
    pytest.main()
