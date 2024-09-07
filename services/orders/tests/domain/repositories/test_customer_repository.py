from unittest.mock import MagicMock

import pytest
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.repositories.customer_repository import CustomerRepository


def test_customer_repository_has_save_method():
    assert hasattr(CustomerRepository, "save")
    assert callable(getattr(CustomerRepository, "save"))


def test_customer_repository_has_find_by_email_method():
    assert hasattr(CustomerRepository, "find_by_email")
    assert callable(getattr(CustomerRepository, "find_by_email"))


def test_customer_repository_has_list_all_method():
    assert hasattr(CustomerRepository, "list_all")
    assert callable(getattr(CustomerRepository, "list_all"))


def test_customer_repository_has_delete_method():
    assert hasattr(CustomerRepository, "delete")
    assert callable(getattr(CustomerRepository, "delete"))


def test_customer_repository_save_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        CustomerRepository().save(MagicMock(spec=CustomerEntity))


def test_customer_repository_find_by_email_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        CustomerRepository().find_by_email("test@example.com")


def test_customer_repository_list_all_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        CustomerRepository().list_all()


def test_customer_repository_delete_raises_not_implemented_error():
    with pytest.raises(NotImplementedError):
        CustomerRepository().delete(MagicMock(spec=CustomerEntity))
