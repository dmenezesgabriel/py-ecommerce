import inspect

import pytest
from src.domain.repositories.order_repository import OrderRepository


class TestOrderRepository:

    def test_has_save_method(self):
        # Arrange & Act
        has_save = inspect.isfunction(OrderRepository.save)

        # Assert
        assert has_save is True
        assert list(
            inspect.signature(OrderRepository.save).parameters.keys()
        ) == ["self", "order"]

    def test_has_find_by_id_method(self):
        # Arrange & Act
        has_find_by_id = inspect.isfunction(OrderRepository.find_by_id)

        # Assert
        assert has_find_by_id is True
        assert list(
            inspect.signature(OrderRepository.find_by_id).parameters.keys()
        ) == ["self", "order_id"]

    def test_has_find_by_order_number_method(self):
        # Arrange & Act
        has_find_by_order_number = inspect.isfunction(
            OrderRepository.find_by_order_number
        )

        # Assert
        assert has_find_by_order_number is True
        assert list(
            inspect.signature(
                OrderRepository.find_by_order_number
            ).parameters.keys()
        ) == ["self", "order_number"]

    def test_has_delete_method(self):
        # Arrange & Act
        has_delete = inspect.isfunction(OrderRepository.delete)

        # Assert
        assert has_delete is True
        assert list(
            inspect.signature(OrderRepository.delete).parameters.keys()
        ) == ["self", "order"]

    def test_has_list_all_method(self):
        # Arrange & Act
        has_list_all = inspect.isfunction(OrderRepository.list_all)

        # Assert
        assert has_list_all is True
        assert list(
            inspect.signature(OrderRepository.list_all).parameters.keys()
        ) == ["self"]

    def test_methods_are_callable(self):
        # Arrange & Act / Assert
        assert callable(getattr(OrderRepository, "save", None))
        assert callable(getattr(OrderRepository, "find_by_id", None))
        assert callable(getattr(OrderRepository, "find_by_order_number", None))
        assert callable(getattr(OrderRepository, "delete", None))
        assert callable(getattr(OrderRepository, "list_all", None))


if __name__ == "__main__":
    pytest.main()
