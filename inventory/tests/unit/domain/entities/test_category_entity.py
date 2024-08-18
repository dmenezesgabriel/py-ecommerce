from unittest.mock import MagicMock, patch

import pytest
from src.domain.entities.category_entity import CategoryEntity
from src.domain.exceptions import InvalidEntity


class TestCategoryEntity:

    def test_create_valid_category(self):
        # Arrange & Act
        category = CategoryEntity(name="Electronics", id=1)

        # Assert
        assert category.id == 1
        assert category.name == "Electronics"

    def test_create_category_invalid_id(self):
        # Arrange & Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            CategoryEntity(name="Electronics", id=-1)

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_create_category_invalid_name(self):
        # Arrange & Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            CategoryEntity(name="", id=1)

        # Assert
        assert "Invalid name" in str(exc_info.value)

    def test_set_valid_id(self):
        # Arrange
        category = CategoryEntity(name="Electronics", id=1)

        # Act
        category.id = 2

        # Assert
        assert category.id == 2

    def test_set_invalid_id(self):
        # Arrange
        category = CategoryEntity(name="Electronics", id=1)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            category.id = -1

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_set_valid_name(self):
        # Arrange
        category = CategoryEntity(name="Electronics", id=1)

        # Act
        category.name = "Home Appliances"

        # Assert
        assert category.name == "Home Appliances"

    def test_set_invalid_name(self):
        # Arrange
        category = CategoryEntity(name="Electronics", id=1)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            category.name = ""

        # Assert
        assert "Invalid name" in str(exc_info.value)

    def test_to_dict(self):
        # Arrange
        category = CategoryEntity(name="Electronics", id=1)

        # Act
        category_dict = category.to_dict()

        # Assert
        assert category_dict == {"id": 1, "name": "Electronics"}


if __name__ == "__main__":
    pytest.main()
