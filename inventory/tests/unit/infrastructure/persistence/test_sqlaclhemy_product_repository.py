from unittest.mock import MagicMock, patch

import pytest
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.inventory_entity import InventoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.entities.product_entity import ProductEntity
from src.infrastructure.persistence.models import (
    CategoryModel,
    InventoryModel,
    PriceModel,
    ProductModel,
)
from src.infrastructure.persistence.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)


class TestSQLAlchemyProductRepository:

    @patch(
        "src.infrastructure.persistence.sqlalchemy_product_repository.CategoryModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_product_repository.ProductModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_product_repository.PriceModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_product_repository.InventoryModel"
    )
    def test_save_new_product(
        self,
        MockInventoryModel,
        MockPriceModel,
        MockProductModel,
        MockCategoryModel,
    ):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyProductRepository(mock_session)

        category = CategoryEntity(id=1, name="Electronics")
        price = PriceEntity(id=1, amount=999.99)
        inventory = InventoryEntity(id=1, quantity=50)
        product = ProductEntity(
            sku="123ABC",
            name="Laptop",
            category=category,
            price=price,
            inventory=inventory,
        )

        mock_category_model_instance = MagicMock(spec=CategoryModel)
        mock_category_model_instance.id = 1
        mock_category_model_instance.name = (
            "Electronics"  # Set a real string value
        )
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_category_model_instance
        )

        mock_product_model_instance = MagicMock(spec=ProductModel)
        mock_product_model_instance.id = 1
        mock_product_model_instance.sku = "123ABC"
        MockProductModel.return_value = mock_product_model_instance

        mock_price_model_instance = MagicMock(spec=PriceModel)
        mock_price_model_instance.id = 1
        mock_price_model_instance.amount = 999.99
        MockPriceModel.return_value = mock_price_model_instance

        mock_inventory_model_instance = MagicMock(spec=InventoryModel)
        mock_inventory_model_instance.id = 1
        mock_inventory_model_instance.quantity = 50
        MockInventoryModel.return_value = mock_inventory_model_instance

        # Act
        result = repository.save(product)

        # Assert
        mock_session.add.assert_called()
        mock_session.commit.assert_called()
        mock_session.refresh.assert_called()

        # Check if the returned ProductEntity matches the expected values
        assert result.id == mock_product_model_instance.id
        assert result.sku == product.sku
        assert result.name == product.name
        assert result.category.name == product.category.name
        assert result.price.amount == product.price.amount
        assert result.inventory.quantity == product.inventory.quantity

    def test_find_by_sku_found(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyProductRepository(mock_session)

        mock_product_model_instance = MagicMock(spec=ProductModel)
        mock_product_model_instance.id = 1
        mock_product_model_instance.sku = "123ABC"
        mock_product_model_instance.name = "Laptop"
        mock_product_model_instance.category_id = 1
        mock_product_model_instance.description = "Laptop device"
        mock_product_model_instance.images = ["https://example.com"]

        # Set valid integers for price and inventory IDs directly
        mock_product_model_instance.price.id = 1
        mock_product_model_instance.price.amount = 999.99
        mock_product_model_instance.inventory.id = 1
        mock_product_model_instance.inventory.quantity = 50

        mock_category_model_instance = MagicMock(spec=CategoryModel)
        mock_category_model_instance.id = 1
        mock_category_model_instance.name = "Electronics"

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_product_model_instance,
            mock_category_model_instance,
        ]

        # Act
        result = repository.find_by_sku("123ABC")

        # Assert
        mock_session.query.assert_any_call(ProductModel)
        mock_session.query.assert_any_call(CategoryModel)

        product_filter_args = (
            mock_session.query.return_value.filter.call_args_list[0][0][0]
        )
        assert str(product_filter_args) == str(ProductModel.sku == "123ABC")

        category_filter_args = (
            mock_session.query.return_value.filter.call_args_list[1][0][0]
        )
        assert str(category_filter_args) == str(CategoryModel.id == 1)

        assert result is not None
        assert result.sku == "123ABC"
        assert result.name == "Laptop"
        assert result.category.name == "Electronics"
        assert result.price.amount == 999.99
        assert result.inventory.quantity == 50
        assert result.description == "Laptop device"
        assert result.images == ["https://example.com"]

    def test_find_by_sku_not_found(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyProductRepository(mock_session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        # Act
        result = repository.find_by_sku("NonExisting")

        # Assert
        mock_session.query.assert_called_with(ProductModel)
        # Check that the filter was called with the correct SKU
        filter_args = mock_session.query().filter.call_args[0][0]
        assert str(filter_args) == str(ProductModel.sku == "NonExisting")
        assert result is None

    def test_delete_product(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyProductRepository(mock_session)

        mock_product_model_instance = MagicMock()
        mock_product_model_instance.id = 1
        mock_product_model_instance.sku = "123ABC"
        mock_product_model_instance.price = MagicMock()
        mock_product_model_instance.price.id = 1
        mock_product_model_instance.inventory = MagicMock()
        mock_product_model_instance.inventory.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_product_model_instance
        )

        # Act
        repository.delete(
            ProductEntity(
                sku="123ABC",
                name="Laptop",
                category=MagicMock(),
                price=MagicMock(),
                inventory=MagicMock(),
            )
        )

        # Assert
        mock_session.delete.assert_called()
        mock_session.commit.assert_called()

    def test_list_all_products(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyProductRepository(mock_session)

        mock_product_model_instance = MagicMock()
        mock_product_model_instance.id = 1
        mock_product_model_instance.sku = "123ABC"
        mock_product_model_instance.name = "Laptop"
        mock_product_model_instance.category = MagicMock()
        mock_product_model_instance.category.id = 1
        mock_product_model_instance.category.name = "Electronics"
        mock_product_model_instance.price = MagicMock()
        mock_product_model_instance.price.id = 1
        mock_product_model_instance.price.amount = 999.99
        mock_product_model_instance.inventory = MagicMock()
        mock_product_model_instance.inventory.id = 1
        mock_product_model_instance.inventory.quantity = 50
        mock_session.query.return_value.all.return_value = [
            mock_product_model_instance
        ]
        mock_product_model_instance.description = "Laptop device"
        mock_product_model_instance.images = ["https://example.com"]

        # Act
        result = repository.list_all()

        # Assert
        mock_session.query.assert_called_with(ProductModel)
        mock_session.query().all.assert_called_once()
        assert len(result) == 1
        assert result[0].sku == "123ABC"
        assert result[0].name == "Laptop"
        assert result[0].category.name == "Electronics"
        assert result[0].price.amount == 999.99
        assert result[0].inventory.quantity == 50
        assert result[0].description == "Laptop device"
        assert result[0].images == ["https://example.com"]

    def test_find_by_category(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyProductRepository(mock_session)

        mock_category_model_instance = MagicMock()
        mock_category_model_instance.id = 1
        mock_category_model_instance.name = "Electronics"
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_category_model_instance
        )

        mock_product_model_instance = MagicMock()
        mock_product_model_instance.id = 1
        mock_product_model_instance.sku = "123ABC"
        mock_product_model_instance.name = "Laptop"
        mock_product_model_instance.category = mock_category_model_instance
        mock_product_model_instance.price = MagicMock()
        mock_product_model_instance.price.id = 1
        mock_product_model_instance.price.amount = 999.99
        mock_product_model_instance.inventory = MagicMock()
        mock_product_model_instance.inventory.id = 1
        mock_product_model_instance.inventory.quantity = 50
        mock_session.query.return_value.filter.return_value.all.return_value = [
            mock_product_model_instance
        ]

        # Act
        result = repository.find_by_category(
            CategoryEntity(id=1, name="Electronics")
        )

        # Assert
        mock_session.query.assert_called_with(ProductModel)
        # Check that the filter was called with the correct category_id
        filter_args = mock_session.query().filter.call_args[0][0]
        assert str(filter_args) == str(ProductModel.category_id == 1)

        assert len(result) == 1
        assert result[0].sku == "123ABC"
        assert result[0].name == "Laptop"
        assert result[0].category.name == "Electronics"
        assert result[0].price.amount == 999.99
        assert result[0].inventory.quantity == 50


if __name__ == "__main__":
    pytest.main()
