from unittest.mock import MagicMock, patch

import pytest
from src.domain.entities.payment_entity import PaymentEntity, PaymentStatus
from src.domain.exceptions import InvalidEntity


def test_payment_entity_initialization():
    entity = PaymentEntity(
        order_id=1,
        amount=100.0,
        status=PaymentStatus.PENDING,
        qr_code="sample_qr_code",
        qr_code_expiration=3600,
        id="sample_id",
    )

    assert entity.id == "sample_id"
    assert entity.order_id == 1
    assert entity.amount == 100.0
    assert entity.status == PaymentStatus.PENDING
    assert entity.qr_code == "sample_qr_code"
    assert entity.qr_code_expiration == 3600


def test_payment_entity_invalid_id():
    with pytest.raises(InvalidEntity):
        PaymentEntity(
            order_id=1,
            amount=100.0,
            status=PaymentStatus.PENDING,
            id=123,  # Invalid ID, should be str or None
        )


def test_payment_entity_invalid_order_id():
    with pytest.raises(InvalidEntity):
        PaymentEntity(
            order_id=-1,  # Invalid order ID, should be positive integer
            amount=100.0,
            status=PaymentStatus.PENDING,
        )


def test_payment_entity_invalid_amount():
    with pytest.raises(InvalidEntity):
        PaymentEntity(
            order_id=1,
            amount=-10.0,  # Invalid amount, should be positive float
            status=PaymentStatus.PENDING,
        )


def test_payment_entity_invalid_status():
    with pytest.raises(InvalidEntity):
        PaymentEntity(
            order_id=1,
            amount=100.0,
            status="invalid_status",  # Invalid status, should be one of PaymentStatus
        )


def test_payment_entity_invalid_qr_code_expiration():
    with pytest.raises(InvalidEntity):
        PaymentEntity(
            order_id=1,
            amount=100.0,
            status=PaymentStatus.PENDING,
            qr_code_expiration=-10,  # Invalid expiration, should be positive integer or None
        )


def test_payment_entity_setters():
    entity = PaymentEntity(
        order_id=1,
        amount=100.0,
        status=PaymentStatus.PENDING,
    )

    entity.id = "new_id"
    assert entity.id == "new_id"

    entity.order_id = 2
    assert entity.order_id == 2

    entity.amount = 200.0
    assert entity.amount == 200.0

    entity.status = PaymentStatus.COMPLETED
    assert entity.status == PaymentStatus.COMPLETED

    entity.qr_code = "new_qr_code"
    assert entity.qr_code == "new_qr_code"

    entity.qr_code_expiration = 7200
    assert entity.qr_code_expiration == 7200


def test_payment_entity_update_status():
    entity = PaymentEntity(
        order_id=1,
        amount=100.0,
        status=PaymentStatus.PENDING,
    )

    entity.update_status(PaymentStatus.COMPLETED)
    assert entity.status == PaymentStatus.COMPLETED


def test_payment_entity_to_dict():
    entity = PaymentEntity(
        order_id=1,
        amount=100.0,
        status=PaymentStatus.PENDING,
        qr_code="sample_qr_code",
        qr_code_expiration=3600,
        id="sample_id",
    )

    entity_dict = entity.to_dict()

    assert entity_dict == {
        "id": "sample_id",
        "order_id": 1,
        "amount": 100.0,
        "status": PaymentStatus.PENDING,
        "qr_code": "sample_qr_code",
        "qr_code_expiration": 3600,
    }
