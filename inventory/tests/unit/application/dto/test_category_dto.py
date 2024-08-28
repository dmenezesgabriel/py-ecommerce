import pytest
from pydantic import ValidationError
from src.application.dto.category_dto import CategoryCreate, CategoryResponse


class TestCategoryCreate:

    def test_create_category_create_valid(self):
        # Arrange & Act
        category = CategoryCreate(name="Food")

        # Assert
        assert category.name == "Food"

    def test_create_category_create_invalid(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            CategoryCreate(name=123)  # Invalid type

    def test_category_create_to_dict(self):
        # Arrange
        category = CategoryCreate(name="Food")

        # Act
        category_dict = category.model_dump()

        # Assert
        assert category_dict == {"name": "Food"}

    def test_category_create_example(self):
        # Arrange & Act
        example = CategoryCreate.model_config["json_schema_extra"]["examples"]

        # Assert
        assert example == [
            {"name": "Food"},
            {"name": "Electronics"},
        ]


class TestCategoryResponse:

    def test_create_category_response_valid(self):
        # Arrange & Act
        category = CategoryResponse(id=1, name="Food")

        # Assert
        assert category.id == 1
        assert category.name == "Food"

    def test_create_category_response_invalid(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            CategoryResponse(id="abc", name="Food")  # Invalid type for id

    def test_category_response_to_dict(self):
        # Arrange
        category = CategoryResponse(id=1, name="Food")

        # Act
        category_dict = category.model_dump()

        # Assert
        assert category_dict == {"id": 1, "name": "Food"}

    def test_category_response_example(self):
        # Arrange & Act
        example = CategoryResponse.model_config["json_schema_extra"][
            "examples"
        ]

        # Assert
        assert example == [
            {"id": 1, "name": "Food"},
            {"id": 2, "name": "Electronics"},
        ]


if __name__ == "__main__":
    pytest.main()
