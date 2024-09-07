from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from src.adapters.api.inventory_api import add_inventory, subtract_inventory
from src.application.dto.inventory_dto import InventoryUpdate
from src.application.dto.product_dto import ProductResponse
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.entities.product_entity import ProductEntity
from src.domain.exceptions import EntityNotFound, InvalidEntity


class TestInventoryAPI:

    @patch("src.adapters.api.inventory_api.get_product_service")
    def test_add_inventory_success(self, mock_get_product_service):
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
        )
        mock_service.add_inventory.return_value = mock_product_entity
        mock_get_product_service.return_value = mock_service

        inventory_update = InventoryUpdate(quantity=10)

        # Act
        response = add_inventory(
            sku="123ABC",
            inventory_update=inventory_update,
            service=mock_service,
        )

        # Assert
        mock_service.add_inventory.assert_called_once_with("123ABC", 10)
        assert response == ProductResponse(
            id=1,
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=50,
        )

    @patch("src.adapters.api.inventory_api.get_product_service")
    def test_subtract_inventory_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category = CategoryEntity(id=1, name="Electronics")
        mock_price = PriceEntity(id=1, amount=999.99)
        mock_inventory = MagicMock(quantity=40)
        mock_product_entity = ProductEntity(
            id=1,
            sku="123ABC",
            name="Laptop",
            category=mock_category,
            price=mock_price,
            inventory=mock_inventory,
        )
        mock_service.subtract_inventory.return_value = mock_product_entity
        mock_get_product_service.return_value = mock_service

        inventory_update = InventoryUpdate(quantity=10)

        # Act
        response = subtract_inventory(
            sku="123ABC",
            inventory_update=inventory_update,
            service=mock_service,
        )

        # Assert
        mock_service.subtract_inventory.assert_called_once_with("123ABC", 10)
        assert response == ProductResponse(
            id=1,
            sku="123ABC",
            name="Laptop",
            category_name="Electronics",
            price=999.99,
            quantity=40,
        )

    @patch("src.adapters.api.inventory_api.get_product_service")
    def test_add_inventory_entity_not_found(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.add_inventory.side_effect = EntityNotFound(
            "Product not found"
        )
        mock_get_product_service.return_value = mock_service

        inventory_update = InventoryUpdate(quantity=10)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            add_inventory(
                sku="123ABC",
                inventory_update=inventory_update,
                service=mock_service,
            )

        mock_service.add_inventory.assert_called_once_with("123ABC", 10)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @patch("src.adapters.api.inventory_api.get_product_service")
    def test_subtract_inventory_entity_not_found(
        self, mock_get_product_service
    ):
        # Arrange
        mock_service = MagicMock()
        mock_service.subtract_inventory.side_effect = EntityNotFound(
            "Product not found"
        )
        mock_get_product_service.return_value = mock_service

        inventory_update = InventoryUpdate(quantity=10)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            subtract_inventory(
                sku="123ABC",
                inventory_update=inventory_update,
                service=mock_service,
            )

        mock_service.subtract_inventory.assert_called_once_with("123ABC", 10)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @patch("src.adapters.api.inventory_api.get_product_service")
    def test_subtract_inventory_invalid_entity(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.subtract_inventory.side_effect = InvalidEntity(
            "Invalid quantity"
        )
        mock_get_product_service.return_value = mock_service

        inventory_update = InventoryUpdate(quantity=10)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            subtract_inventory(
                sku="123ABC",
                inventory_update=inventory_update,
                service=mock_service,
            )

        mock_service.subtract_inventory.assert_called_once_with("123ABC", 10)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid quantity"


if __name__ == "__main__":
    pytest.main()
