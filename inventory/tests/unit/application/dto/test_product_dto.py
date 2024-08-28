import pytest
from pydantic import ValidationError
from src.application.dto.product_dto import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)


class TestProductCreate:

    def test_create_product_create_valid(self):
        # Arrange & Act
        product = ProductCreate(
            sku="123",
            name="Potato Sauce",
            category_name="Food",
            price=1.50,
            quantity=100,
        )

        # Assert
        assert product.sku == "123"
        assert product.name == "Potato Sauce"
        assert product.category_name == "Food"
        assert product.price == 1.50
        assert product.quantity == 100

    def test_create_product_create_invalid(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            ProductCreate(
                sku=123,
                name=456,
                category_name="Food",
                price="1.50",
                quantity="100",
            )  # Invalid types

    def test_product_create_to_dict(self):
        # Arrange
        product = ProductCreate(
            sku="123",
            name="Potato Sauce",
            category_name="Food",
            price=1.50,
            quantity=100,
            images=["http://example.com"],
            description="Awesome sauce",
        )

        # Act
        product_dict = product.model_dump()

        # Assert
        assert product_dict == {
            "sku": "123",
            "name": "Potato Sauce",
            "category_name": "Food",
            "price": 1.50,
            "quantity": 100,
            "images": ["http://example.com"],
            "description": "Awesome sauce",
        }

    def test_product_create_example(self):
        # Arrange & Act
        example = ProductCreate.model_config["json_schema_extra"]["examples"]

        # Assert
        assert example == [
            {
                "sku": "123",
                "name": "Potato Sauce",
                "description": "Nice tasty potato sauce",
                "category_name": "Food",
                "price": 1.50,
                "quantity": 100,
                "images": ["https://example1.com", "https://example2.com"],
            }
        ]


class TestProductUpdate:

    def test_create_product_update_valid(self):
        # Arrange & Act
        product = ProductUpdate(
            name="Potato Sauce", category_name="Food", price=1.50, quantity=150
        )

        # Assert
        assert product.name == "Potato Sauce"
        assert product.category_name == "Food"
        assert product.price == 1.50
        assert product.quantity == 150

    def test_create_product_update_invalid(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            ProductUpdate(
                name=123, category_name=456, price="1.50", quantity="150"
            )  # Invalid types

    def test_product_update_to_dict(self):
        # Arrange
        product = ProductUpdate(
            name="Potato Sauce",
            category_name="Food",
            price=1.50,
            quantity=150,
            images=["http://example.com"],
            description="Awesome sauce",
        )

        # Act
        product_dict = product.model_dump()

        # Assert
        assert product_dict == {
            "name": "Potato Sauce",
            "category_name": "Food",
            "price": 1.50,
            "quantity": 150,
            "images": ["http://example.com"],
            "description": "Awesome sauce",
        }

    def test_product_update_example(self):
        # Arrange & Act
        example = ProductUpdate.model_config["json_schema_extra"]["examples"]

        # Assert
        assert example == [
            {
                "name": "(Updated) Potato Sauce",
                "description": "(Updated) Nice tasty potato sauce",
                "category_name": "Food",
                "price": 1.50,
                "quantity": 150,
                "images": ["https://example1.com", "https://example2.com"],
            }
        ]


class TestProductResponse:

    def test_create_product_response_valid(self):
        # Arrange & Act
        product = ProductResponse(
            sku="123",
            name="Potato Sauce",
            category_name="Food",
            price=1.50,
            quantity=100,
        )

        # Assert
        assert product.sku == "123"
        assert product.name == "Potato Sauce"
        assert product.category_name == "Food"
        assert product.price == 1.50
        assert product.quantity == 100

    def test_create_product_response_invalid(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            ProductResponse(
                sku=123,
                name=456,
                category_name="Food",
                price="1.50",
                quantity="100",
            )  # Invalid types

    def test_product_response_to_dict(self):
        # Arrange
        product = ProductResponse(
            sku="123",
            name="Potato Sauce",
            category_name="Food",
            price=1.50,
            quantity=100,
            images=["http://example.com"],
            description="Awesome sauce",
        )

        # Act
        product_dict = product.model_dump()

        # Assert
        assert product_dict == {
            "sku": "123",
            "name": "Potato Sauce",
            "category_name": "Food",
            "price": 1.50,
            "quantity": 100,
            "images": ["http://example.com"],
            "description": "Awesome sauce",
        }

    def test_product_response_example(self):
        # Arrange & Act
        example = ProductResponse.model_config["json_schema_extra"]["examples"]

        # Assert
        assert example == [
            {
                "sku": "123",
                "name": "Potato Sauce",
                "description": "Nice tasty potato sauce",
                "category_name": "Food",
                "price": 1.50,
                "quantity": 100,
                "images": ["https://example.com", "https://example.com"],
            }
        ]


if __name__ == "__main__":
    pytest.main()
