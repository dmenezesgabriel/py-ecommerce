from unittest.mock import MagicMock

from src.domain.entities.payment_entity import PaymentEntity
from src.domain.repositories.payment_repository import PaymentRepository


def test_payment_repository_methods_exist():
    # Create a mock instance of the PaymentRepository
    repository = MagicMock(spec=PaymentRepository)

    # Test that the save method exists and is callable
    assert hasattr(repository, "save")
    assert callable(repository.save)

    # Test that the find_by_id method exists and is callable
    assert hasattr(repository, "find_by_id")
    assert callable(repository.find_by_id)

    # Test that the find_by_order_id method exists and is callable
    assert hasattr(repository, "find_by_order_id")
    assert callable(repository.find_by_order_id)

    # Test that the delete method exists and is callable
    assert hasattr(repository, "delete")
    assert callable(repository.delete)


def test_payment_repository_save():
    # Create a mock instance of the PaymentRepository
    repository = MagicMock(spec=PaymentRepository)

    # Create a mock payment entity
    payment = MagicMock(spec=PaymentEntity)

    # Call the save method with the mock payment entity
    repository.save(payment)

    # Verify that the save method was called once with the mock payment entity
    repository.save.assert_called_once_with(payment)


def test_payment_repository_find_by_id():
    # Create a mock instance of the PaymentRepository
    repository = MagicMock(spec=PaymentRepository)

    # Call the find_by_id method with a mock payment ID
    payment_id = "sample_payment_id"
    repository.find_by_id(payment_id)

    # Verify that the find_by_id method was called once with the mock payment ID
    repository.find_by_id.assert_called_once_with(payment_id)


def test_payment_repository_find_by_order_id():
    # Create a mock instance of the PaymentRepository
    repository = MagicMock(spec=PaymentRepository)

    # Call the find_by_order_id method with a mock order ID
    order_id = 123
    repository.find_by_order_id(order_id)

    # Verify that the find_by_order_id method was called once with the mock order ID
    repository.find_by_order_id.assert_called_once_with(order_id)


def test_payment_repository_delete():
    # Create a mock instance of the PaymentRepository
    repository = MagicMock(spec=PaymentRepository)

    # Create a mock payment entity
    payment = MagicMock(spec=PaymentEntity)

    # Call the delete method with the mock payment entity
    repository.delete(payment)

    # Verify that the delete method was called once with the mock payment entity
    repository.delete.assert_called_once_with(payment)
