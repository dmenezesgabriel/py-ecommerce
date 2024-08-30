from unittest.mock import MagicMock, patch

import pytest
from bson.objectid import ObjectId
from src.domain.entities.payment_entity import PaymentEntity
from src.infrastructure.persistence.mongo_payment_repository import (
    MongoDBPaymentRepository,
)


def test_save_new_payment():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    payment = PaymentEntity(order_id=1, amount=100.0, status="pending")

    mock_result = MagicMock(inserted_id=ObjectId())
    mock_db.insert_one.return_value = mock_result

    repository.save(payment)

    mock_db.insert_one.assert_called_once_with(payment.__dict__)
    assert payment.id == str(mock_result.inserted_id)


def test_save_existing_payment():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    payment = PaymentEntity(
        id=str(ObjectId()), order_id=1, amount=100.0, status="pending"
    )

    repository.save(payment)

    mock_db.replace_one.assert_called_once_with(
        {"_id": ObjectId(payment.id)}, payment.__dict__
    )


def test_find_by_id_exists():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    payment_id = str(ObjectId())
    payment_data = {
        "_id": ObjectId(payment_id),
        "order_id": 1,
        "amount": 100.0,
        "status": "pending",
        "qr_code": "some_qr_code",
        "qr_code_expiration": 1234567890,
    }

    mock_db.find_one.return_value = payment_data

    payment = repository.find_by_id(payment_id)

    assert payment is not None
    assert payment.id == payment_id
    assert payment.order_id == 1
    assert payment.amount == 100.0
    assert payment.status == "pending"
    assert payment.qr_code == "some_qr_code"
    assert payment.qr_code_expiration == 1234567890


def test_find_by_id_not_exists():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    mock_db.find_one.return_value = None

    payment = repository.find_by_id(str(ObjectId()))

    assert payment is None


def test_find_by_order_id_exists():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    order_id = 1
    payment_data = {
        "_id": ObjectId(),
        "order_id": order_id,
        "amount": 100.0,
        "status": "pending",
        "qr_code": "some_qr_code",
        "qr_code_expiration": 1234567890,
    }

    mock_db.find_one.return_value = payment_data

    payment = repository.find_by_order_id(order_id)

    assert payment is not None
    assert payment.order_id == order_id
    assert payment.amount == 100.0
    assert payment.status == "pending"
    assert payment.qr_code == "some_qr_code"
    assert payment.qr_code_expiration == 1234567890


def test_find_by_order_id_not_exists():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    mock_db.find_one.return_value = None

    payment = repository.find_by_order_id(1)

    assert payment is None


def test_delete_payment():
    mock_db = MagicMock()
    repository = MongoDBPaymentRepository(mock_db)

    payment = PaymentEntity(
        id=str(ObjectId()), order_id=1, amount=100.0, status="pending"
    )

    repository.delete(payment)

    mock_db.delete_one.assert_called_once_with({"_id": ObjectId(payment.id)})
