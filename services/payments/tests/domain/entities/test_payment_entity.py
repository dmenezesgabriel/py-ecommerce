from unittest.mock import patch

import pytest
from src.domain.entities.payment_entity import PaymentEntity, PaymentStatus


def test_payment_entity_creation():
    # Arrange
    order_id = 1
    amount = 100.0
    status = PaymentStatus.PENDING
    qr_code = "sample_qr_code"
    qr_code_expiration = 1234567890
    payment_id = "sample_id"

    # Act
    payment = PaymentEntity(
        order_id=order_id,
        amount=amount,
        status=status,
        qr_code=qr_code,
        qr_code_expiration=qr_code_expiration,
        id=payment_id,
    )

    # Assert
    assert payment.id == payment_id
    assert payment.order_id == order_id
    assert payment.amount == amount
    assert payment.status == status
    assert payment.qr_code == qr_code
    assert payment.qr_code_expiration == qr_code_expiration


def test_payment_entity_default_values():
    # Arrange
    order_id = 2
    amount = 200.0
    status = PaymentStatus.PENDING

    # Act
    payment = PaymentEntity(
        order_id=order_id,
        amount=amount,
        status=status,
    )

    # Assert
    assert payment.id is None
    assert payment.qr_code is None
    assert payment.qr_code_expiration is None


def test_payment_entity_update_status():
    # Arrange
    order_id = 3
    amount = 300.0
    status = PaymentStatus.PENDING
    payment = PaymentEntity(
        order_id=order_id,
        amount=amount,
        status=status,
    )

    # Act
    new_status = PaymentStatus.COMPLETED
    payment.update_status(new_status)

    # Assert
    assert payment.status == new_status


@patch("src.domain.entities.payment_entity.PaymentEntity.update_status")
def test_payment_entity_update_status_mock(mock_update_status):
    # Arrange
    order_id = 4
    amount = 400.0
    status = PaymentStatus.PENDING
    payment = PaymentEntity(
        order_id=order_id,
        amount=amount,
        status=status,
    )

    # Act
    new_status = PaymentStatus.FAILED
    payment.update_status(new_status)

    # Assert
    mock_update_status.assert_called_once_with(new_status)
