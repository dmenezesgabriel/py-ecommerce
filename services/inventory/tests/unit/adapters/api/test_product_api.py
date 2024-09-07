from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from src.adapters.api.product_api import (
    create_product,
    delete_product,
    get_products_by_category,
    read_product,
    update_product,
)
from src.application.dto.product_dto import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.entities.product_entity import ProductEntity
from src.domain.exceptions import EntityAlreadyExists, EntityNotFound


class TestProductAPI:

    @patch("src.adapters.api.product_api.get_product_service")
    def test_create_product_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category = CategoryEntity(id=1, name="Electronics")
        mock_price = PriceEntity(id=1, amount=999.99)
        mock_inventory = MagicMock(quantity=50)
        mock_product_entity = ProductEntity(
            id=1,
            sku="123ABC",
            name="Laptop",
            category=mock_category,
            price=mock_price,
            inventory=mock_inventory,
            images=["http://example.com"],
            description="Laptop device",
        )
        mock_service.create_product.return_value = mock_product_entity
        mock_get_product_service.return_value = mock_service

        product_dto = ProductCreate(
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Laptop device",
        )

        # Act
        response = create_product(product=product_dto, service=mock_service)

        # Assert
        mock_service.create_product.assert_called_once_with(
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Laptop device",
        )
        assert response == ProductResponse(
            id=1,
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Laptop device",
        )

    @patch("src.adapters.api.product_api.get_product_service")
    def test_create_product_already_exists(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.create_product.side_effect = EntityAlreadyExists(
            "Product already exists"
        )
        mock_get_product_service.return_value = mock_service

        product_dto = ProductCreate(
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Laptop device",
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_product(product=product_dto, service=mock_service)

        mock_service.create_product.assert_called_once_with(
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Laptop device",
        )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Product already exists"

    @patch("src.adapters.api.product_api.get_product_service")
    def test_read_product_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category = CategoryEntity(id=1, name="Electronics")
        mock_price = PriceEntity(id=1, amount=999.99)
        mock_inventory = MagicMock(quantity=50)
        mock_product_entity = ProductEntity(
            id=1,
            sku="123ABC",
            name="Laptop",
            category=mock_category,
            price=mock_price,
            inventory=mock_inventory,
            images=["http://example.com"],
            description="Smartphone device",
        )
        mock_service.get_product_by_sku.return_value = mock_product_entity
        mock_get_product_service.return_value = mock_service

        # Act
        response = read_product(sku="123ABC", service=mock_service)

        # Assert
        mock_service.get_product_by_sku.assert_called_once_with("123ABC")
        assert response == ProductResponse(
            id=1,
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Smartphone device",
        )

    @patch("src.adapters.api.product_api.get_product_service")
    def test_read_product_not_found(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.get_product_by_sku.side_effect = EntityNotFound(
            "Product not found"
        )
        mock_get_product_service.return_value = mock_service

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            read_product(sku="123ABC", service=mock_service)

        mock_service.get_product_by_sku.assert_called_once_with("123ABC")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @patch("src.adapters.api.product_api.get_product_service")
    def test_update_product_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category = CategoryEntity(id=1, name="Electronics")
        mock_price = PriceEntity(id=1, amount=999.99)
        mock_inventory = MagicMock(quantity=60)
        mock_product_entity = ProductEntity(
            id=1,
            sku="123ABC",
            name="Laptop Pro",
            category=mock_category,
            price=mock_price,
            inventory=mock_inventory,
            images=["http://example.com"],
            description="Smartphone device",
        )
        mock_service.update_product.return_value = mock_product_entity
        mock_get_product_service.return_value = mock_service

        product_update_dto = ProductUpdate(
            name="Laptop Pro",
            category_name="Electronics",
            price=999.99,
            quantity=60,
            images=["http://example.com"],
            description="Smartphone device",
        )

        # Act
        response = update_product(
            sku="123ABC",
            product=product_update_dto,
            service=mock_service,
        )

        # Assert
        mock_service.update_product.assert_called_once_with(
            sku="123ABC",
            name="Laptop Pro",
            category_name="Electronics",
            price=999.99,
            quantity=60,
            images=["http://example.com"],
            description="Smartphone device",
        )
        assert response == ProductResponse(
            id=1,
            sku="123ABC",
            name="Laptop Pro",
            category_name="Electronics",
            price=999.99,
            quantity=60,
            images=["http://example.com"],
            description="Smartphone device",
        )

    @patch("src.adapters.api.product_api.get_product_service")
    def test_update_product_not_found(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.update_product.side_effect = EntityNotFound(
            "Product not found"
        )
        mock_get_product_service.return_value = mock_service

        product_update_dto = ProductUpdate(
            name="Laptop Pro",
            category_name="Electronics",
            price=999.99,
            quantity=60,
            images=["http://example.com"],
            description="Smartphone device",
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_product(
                sku="123ABC",
                product=product_update_dto,
                service=mock_service,
            )

        mock_service.update_product.assert_called_once_with(
            sku="123ABC",
            name="Laptop Pro",
            category_name="Electronics",
            price=999.99,
            quantity=60,
            images=["http://example.com"],
            description="Smartphone device",
        )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @patch("src.adapters.api.product_api.get_product_service")
    def test_delete_product_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category = CategoryEntity(id=1, name="Electronics")
        mock_price = PriceEntity(id=1, amount=999.99)
        mock_inventory = MagicMock(quantity=50)
        mock_product_entity = ProductEntity(
            id=1,
            sku="123ABC",
            name="Laptop",
            category=mock_category,
            price=mock_price,
            inventory=mock_inventory,
            images=["http://example.com"],
            description="Smartphone device",
        )
        mock_service.delete_product.return_value = mock_product_entity
        mock_get_product_service.return_value = mock_service

        # Act
        response = delete_product(sku="123ABC", service=mock_service)

        # Assert
        mock_service.delete_product.assert_called_once_with("123ABC")
        assert response == ProductResponse(
            id=1,
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
            images=["http://example.com"],
            description="Smartphone device",
        )

    @patch("src.adapters.api.product_api.get_product_service")
    def test_delete_product_not_found(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.delete_product.side_effect = EntityNotFound(
            "Product not found"
        )
        mock_get_product_service.return_value = mock_service

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_product(sku="123ABC", service=mock_service)

        mock_service.delete_product.assert_called_once_with("123ABC")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @patch("src.adapters.api.product_api.get_product_service")
    def test_get_products_by_category_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category = CategoryEntity(id=1, name="Electronics")
        mock_price = PriceEntity(id=1, amount=999.99)
        mock_inventory = MagicMock(quantity=50)
        mock_product_entities = [
            ProductEntity(
                id=1,
                sku="123ABC",
                name="Laptop",
                category=mock_category,
                price=mock_price,
                inventory=mock_inventory,
                images=["http://example.com"],
                description="Laptop device",
            ),
            ProductEntity(
                id=2,
                sku="456DEF",
                name="Smartphone",
                category=mock_category,
                price=mock_price,
                inventory=MagicMock(quantity=100),
                images=["http://example.com"],
                description="Smartphone device",
            ),
        ]
        mock_service.get_products_by_category.return_value = (
            mock_product_entities
        )
        mock_get_product_service.return_value = mock_service

        # Act
        response = get_products_by_category(
            category_name="Electronics", service=mock_service
        )

        # Assert
        mock_service.get_products_by_category.assert_called_once_with(
            "Electronics"
        )
        assert response == [
            ProductResponse(
                id=1,
                sku="123ABC",
                name="Laptop",
                category_name="Electronics",
                price=999.99,
                quantity=50,
                images=["http://example.com"],
                description="Laptop device",
            ),
            ProductResponse(
                id=2,
                sku="456DEF",
                name="Smartphone",
                category_name="Electronics",
                price=999.99,
                quantity=100,
                images=["http://example.com"],
                description="Smartphone device",
            ),
        ]

    @patch("src.adapters.api.product_api.get_product_service")
    def test_get_products_by_category_not_found(
        self, mock_get_product_service
    ):
        # Arrange
        mock_service = MagicMock()
        mock_service.get_products_by_category.side_effect = EntityNotFound(
            "Category not found"
        )
        mock_get_product_service.return_value = mock_service

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_products_by_category(
                category_name="NonExistingCategory", service=mock_service
            )

        mock_service.get_products_by_category.assert_called_once_with(
            "NonExistingCategory"
        )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Category not found"


if __name__ == "__main__":
    pytest.main()
