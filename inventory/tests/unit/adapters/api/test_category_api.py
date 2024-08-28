from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from src.adapters.api.category_api import create_category
from src.application.dto.category_dto import CategoryCreate, CategoryResponse
from src.domain.entities.category_entity import CategoryEntity
from src.domain.exceptions import EntityAlreadyExists


class TestCategoryAPI:

    @patch("src.adapters.api.category_api.get_product_service")
    def test_create_category_success(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_category_entity = CategoryEntity(id=1, name="Electronics")
        mock_service.create_category.return_value = mock_category_entity
        mock_get_product_service.return_value = mock_service

        category_dto = CategoryCreate(name="Electronics")

        # Act
        response = create_category(category=category_dto, service=mock_service)

        # Assert
        mock_service.create_category.assert_called_once_with(
            name="Electronics"
        )
        assert response == CategoryResponse(id=1, name="Electronics")

    @patch("src.adapters.api.category_api.get_product_service")
    def test_create_category_already_exists(self, mock_get_product_service):
        # Arrange
        mock_service = MagicMock()
        mock_service.create_category.side_effect = EntityAlreadyExists(
            "Category already exists"
        )
        mock_get_product_service.return_value = mock_service

        category_dto = CategoryCreate(name="Electronics")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_category(category=category_dto, service=mock_service)

        mock_service.create_category.assert_called_once_with(
            name="Electronics"
        )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Category already exists"


if __name__ == "__main__":
    pytest.main()
