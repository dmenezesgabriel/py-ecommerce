from unittest.mock import Mock

import pytest
from src.application.services.product_service import ProductService
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.product_entity import ProductEntity
from src.domain.exceptions import EntityAlreadyExists, EntityNotFound
from src.domain.repositories.category_repository import CategoryRepository
from src.domain.repositories.product_repository import ProductRepository


class TestProductService:

    def test_create_product(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        category_repo.find_by_name.return_value = None
        product_repo.find_by_sku.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act
        product = service.create_product(
            sku="123",
            name="Potato Sauce",
            category_name="Food",
            price=1.50,
            quantity=100,
        )

        # Assert
        assert isinstance(product, ProductEntity)
        category_repo.save.assert_called_once()
        product_repo.save.assert_called_once()

    def test_create_product_already_exists(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        product_repo.find_by_sku.return_value = Mock(spec=ProductEntity)
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityAlreadyExists):
            service.create_product(
                sku="123",
                name="Potato Sauce",
                category_name="Food",
                price=1.50,
                quantity=100,
            )

    def test_get_product_by_sku(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product = Mock(spec=ProductEntity)
        product_repo.find_by_sku.return_value = product
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.get_product_by_sku("123")

        # Assert
        assert result == product

    def test_get_product_by_sku_not_found(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product_repo.find_by_sku.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityNotFound):
            service.get_product_by_sku("123")

    def test_update_product(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        category = Mock(spec=CategoryEntity)
        product = Mock(spec=ProductEntity)
        product_repo.find_by_sku.return_value = product
        category_repo.find_by_name.return_value = category
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.update_product(
            sku="123",
            name="Tomato Sauce",
            category_name="Food",
            price=2.00,
            quantity=150,
        )

        # Assert
        assert result == product
        product_repo.save.assert_called_once()
        assert product.set_price.call_count == 1
        assert product.set_inventory.call_count == 1

    def test_update_product_not_found(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product_repo.find_by_sku.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityNotFound):
            service.update_product(
                sku="123",
                name="Tomato Sauce",
                category_name="Food",
                price=2.00,
                quantity=150,
            )

    def test_delete_product(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product = Mock(spec=ProductEntity)
        product_repo.find_by_sku.return_value = product
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.delete_product("123")

        # Assert
        assert result == product
        product_repo.delete.assert_called_once_with(product)

    def test_delete_product_not_found(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product_repo.find_by_sku.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityNotFound):
            service.delete_product("123")

    def test_list_products(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.list_products()

        # Assert
        product_repo.list_all.assert_called_once()
        assert result == product_repo.list_all.return_value

    def test_get_products_by_category(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        category = Mock(spec=CategoryEntity)
        category_repo.find_by_name.return_value = category
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.get_products_by_category("Food")

        # Assert
        product_repo.find_by_category.assert_called_once_with(category)
        assert result == product_repo.find_by_category.return_value

    def test_get_products_by_category_not_found(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        category_repo.find_by_name.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityNotFound):
            service.get_products_by_category("Nonexistent Category")

    def test_add_inventory(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product = Mock(spec=ProductEntity)
        product_repo.find_by_sku.return_value = product
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.add_inventory("123", 50)

        # Assert
        assert result == product
        product_repo.save.assert_called_once()
        product.add_inventory.assert_called_once_with(50)

    def test_add_inventory_not_found(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product_repo.find_by_sku.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityNotFound):
            service.add_inventory("123", 50)

    def test_subtract_inventory(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product = Mock(spec=ProductEntity)
        product_repo.find_by_sku.return_value = product
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.subtract_inventory("123", 50)

        # Assert
        assert result == product
        product_repo.save.assert_called_once()
        product.subtract_inventory.assert_called_once_with(50)

    def test_subtract_inventory_not_found(self):
        # Arrange
        product_repo = Mock(spec=ProductRepository)
        category_repo = Mock(spec=CategoryRepository)
        product_repo.find_by_sku.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityNotFound):
            service.subtract_inventory("123", 50)

    def test_create_category(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        category_repo.find_by_name.return_value = None
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.create_category("Food")

        # Assert
        assert isinstance(result, CategoryEntity)
        category_repo.save.assert_called_once()

    def test_create_category_already_exists(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        category_repo.find_by_name.return_value = Mock(spec=CategoryEntity)
        service = ProductService(product_repo, category_repo)

        # Act / Assert
        with pytest.raises(EntityAlreadyExists):
            service.create_category("Food")

    def test_list_categories(self):
        # Arrange
        category_repo = Mock(spec=CategoryRepository)
        product_repo = Mock(spec=ProductRepository)
        service = ProductService(product_repo, category_repo)

        # Act
        result = service.list_categories()

        # Assert
        category_repo.list_all.assert_called_once()
        assert result == category_repo.list_all.return_value


if __name__ == "__main__":
    pytest.main()
