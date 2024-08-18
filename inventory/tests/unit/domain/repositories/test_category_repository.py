import inspect

import pytest
from src.domain.repositories.category_repository import CategoryRepository


class TestCategoryRepository:

    def test_has_save_method(self):
        # Arrange & Act
        has_save = inspect.isfunction(CategoryRepository.save)

        # Assert
        assert has_save is True
        assert list(
            inspect.signature(CategoryRepository.save).parameters.keys()
        ) == ["self", "category"]

    def test_has_find_by_name_method(self):
        # Arrange & Act
        has_find_by_name = inspect.isfunction(CategoryRepository.find_by_name)

        # Assert
        assert has_find_by_name is True
        assert list(
            inspect.signature(
                CategoryRepository.find_by_name
            ).parameters.keys()
        ) == ["self", "name"]

    def test_has_list_all_method(self):
        # Arrange & Act
        has_list_all = inspect.isfunction(CategoryRepository.list_all)

        # Assert
        assert has_list_all is True
        assert list(
            inspect.signature(CategoryRepository.list_all).parameters.keys()
        ) == ["self"]

    def test_methods_are_callable(self):
        # Arrange & Act / Assert
        assert callable(getattr(CategoryRepository, "save", None))
        assert callable(getattr(CategoryRepository, "find_by_name", None))
        assert callable(getattr(CategoryRepository, "list_all", None))


if __name__ == "__main__":
    pytest.main()
