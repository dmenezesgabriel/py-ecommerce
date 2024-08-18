import inspect

import pytest
from src.domain.repositories.customer_repository import CustomerRepository


class TestCustomerRepository:

    def test_has_save_method(self):
        # Arrange & Act
        has_save = inspect.isfunction(CustomerRepository.save)

        # Assert
        assert has_save is True
        assert list(
            inspect.signature(CustomerRepository.save).parameters.keys()
        ) == ["self", "customer"]

    def test_has_find_by_email_method(self):
        # Arrange & Act
        has_find_by_email = inspect.isfunction(
            CustomerRepository.find_by_email
        )

        # Assert
        assert has_find_by_email is True
        assert list(
            inspect.signature(
                CustomerRepository.find_by_email
            ).parameters.keys()
        ) == ["self", "email"]

    def test_has_list_all_method(self):
        # Arrange & Act
        has_list_all = inspect.isfunction(CustomerRepository.list_all)

        # Assert
        assert has_list_all is True
        assert list(
            inspect.signature(CustomerRepository.list_all).parameters.keys()
        ) == ["self"]

    def test_has_delete_method(self):
        # Arrange & Act
        has_delete = inspect.isfunction(CustomerRepository.delete)

        # Assert
        assert has_delete is True
        assert list(
            inspect.signature(CustomerRepository.delete).parameters.keys()
        ) == ["self", "customer"]

    def test_methods_are_callable(self):
        # Arrange & Act / Assert
        assert callable(getattr(CustomerRepository, "save", None))
        assert callable(getattr(CustomerRepository, "find_by_email", None))
        assert callable(getattr(CustomerRepository, "list_all", None))
        assert callable(getattr(CustomerRepository, "delete", None))


if __name__ == "__main__":
    pytest.main()
