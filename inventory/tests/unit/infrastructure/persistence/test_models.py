from unittest.mock import Mock

import pytest
from src.infrastructure.persistence.models import (
    CategoryModel,
    InventoryModel,
    PriceModel,
    ProductModel,
)


class TestModels:
    def test_category_model_attributes(self):
        # Arrange & Act
        category = CategoryModel()

        # Assert
        assert hasattr(category, "id")
        assert hasattr(category, "name")
        assert hasattr(category, "products")
        assert isinstance(
            category.products, list
        )  # relationship should be a list

    def test_product_model_attributes(self):
        # Arrange & Act
        product = ProductModel()

        # Assert
        assert hasattr(product, "id")
        assert hasattr(product, "sku")
        assert hasattr(product, "name")
        assert hasattr(product, "category_id")
        assert hasattr(product, "category")
        assert hasattr(product, "price")
        assert hasattr(product, "inventory")
        assert product.price is None  # One-to-one relationship starts as None
        assert (
            product.inventory is None
        )  # One-to-one relationship starts as None

    def test_price_model_attributes(self):
        # Arrange & Act
        price = PriceModel()

        # Assert
        assert hasattr(price, "id")
        assert hasattr(price, "product_id")
        assert hasattr(price, "amount")
        assert hasattr(price, "product")
        assert price.product is None  # One-to-one relationship starts as None

    def test_inventory_model_attributes(self):
        # Arrange & Act
        inventory = InventoryModel()

        # Assert
        assert hasattr(inventory, "id")
        assert hasattr(inventory, "product_id")
        assert hasattr(inventory, "quantity")
        assert hasattr(inventory, "product")
        assert (
            inventory.product is None
        )  # One-to-one relationship starts as None


if __name__ == "__main__":
    pytest.main()
