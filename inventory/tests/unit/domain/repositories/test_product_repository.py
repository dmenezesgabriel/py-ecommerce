import inspect

import pytest
from src.domain.repositories.product_repository import ProductRepository


class TestProductRepository:

    def test_has_save_method(self):
        # Arrange & Act
        has_save = inspect.isfunction(ProductRepository.save)

        # Assert
        assert has_save is True
        assert list(
            inspect.signature(ProductRepository.save).parameters.keys()
        ) == ["self", "product"]

    def test_has_find_by_sku_method(self):
        # Arrange & Act
        has_find_by_sku = inspect.isfunction(ProductRepository.find_by_sku)

        # Assert
        assert has_find_by_sku is True
        assert list(
            inspect.signature(ProductRepository.find_by_sku).parameters.keys()
        ) == ["self", "sku"]

    def test_has_delete_method(self):
        # Arrange & Act
        has_delete = inspect.isfunction(ProductRepository.delete)

        # Assert
        assert has_delete is True
        assert list(
            inspect.signature(ProductRepository.delete).parameters.keys()
        ) == ["self", "product"]

    def test_has_list_all_method(self):
        # Arrange & Act
        has_list_all = inspect.isfunction(ProductRepository.list_all)

        # Assert
        assert has_list_all is True
        assert list(
            inspect.signature(ProductRepository.list_all).parameters.keys()
        ) == ["self"]

    def test_has_find_by_category_method(self):
        # Arrange & Act
        has_find_by_category = inspect.isfunction(
            ProductRepository.find_by_category
        )

        # Assert
        assert has_find_by_category is True
        assert list(
            inspect.signature(
                ProductRepository.find_by_category
            ).parameters.keys()
        ) == ["self", "category"]

    def test_methods_are_callable(self):
        # Arrange & Act / Assert
        assert callable(getattr(ProductRepository, "save", None))
        assert callable(getattr(ProductRepository, "find_by_sku", None))
        assert callable(getattr(ProductRepository, "delete", None))
        assert callable(getattr(ProductRepository, "list_all", None))
        assert callable(getattr(ProductRepository, "find_by_category", None))


if __name__ == "__main__":
    pytest.main()
