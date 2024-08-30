from unittest.mock import MagicMock, patch

import pytest
from src.adapters.api.payment_api import (
    create_payment,
    delete_payment,
    handle_webhook,
    read_payment,
    read_payment_by_order_id,
    read_payments,
    update_payment,
)
from src.application.dto.payment_dto import (
    PaymentCreate,
    PaymentUpdate,
    WebhookPayload,
)
from src.application.dto.serializers import serialize_payment
from src.application.services.payment_service import PaymentService
from src.domain.entities.payment_entity import PaymentEntity
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidAction,
)


@patch("src.adapters.api.payment_api.get_payment_service")
def test_create_payment_success(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_payment = PaymentCreate(order_id=1, amount=100.0, status="pending")
    mock_payment_entity = PaymentEntity(
        id="123",
        order_id=1,
        amount=100.0,
        status="pending",
        qr_code="fake_qr",
        qr_code_expiration=3600,
    )
    mock_service.create_payment.return_value = mock_payment_entity

    response = create_payment(payment=mock_payment, service=mock_service)

    mock_service.create_payment.assert_called_once_with(
        order_id=mock_payment.order_id,
        amount=mock_payment.amount,
        status=mock_payment.status,
    )
    assert response == serialize_payment(mock_payment_entity)


@patch("src.adapters.api.payment_api.get_payment_service")
def test_create_payment_already_exists(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_payment = PaymentCreate(order_id=1, amount=100.0, status="pending")
    mock_service.create_payment.side_effect = EntityAlreadyExists(
        "Payment already exists"
    )

    with pytest.raises(Exception) as exc_info:
        create_payment(payment=mock_payment, service=mock_service)

    mock_service.create_payment.assert_called_once_with(
        order_id=mock_payment.order_id,
        amount=mock_payment.amount,
        status=mock_payment.status,
    )
    assert exc_info.value.status_code == 400
    assert str(exc_info.value.detail) == "Payment already exists"


@patch("src.adapters.api.payment_api.get_payment_service")
def test_read_payments(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_service.payment_repository = MagicMock()
    mock_get_payment_service.return_value = mock_service

    mock_payment_entity = {
        "_id": "123",
        "order_id": 1,
        "amount": 100.0,
        "status": "pending",
        "qr_code": "fake_qr",
        "qr_code_expiration": 3600,
    }
    mock_service.payment_repository.db.find.return_value = [
        mock_payment_entity
    ]

    response = read_payments(service=mock_service)

    mock_service.payment_repository.db.find.assert_called_once()
    assert response == [
        serialize_payment(
            PaymentEntity(
                id=mock_payment_entity["_id"],
                **{
                    key: value
                    for key, value in mock_payment_entity.items()
                    if key != "_id"
                }
            )
        )
    ]


@patch("src.adapters.api.payment_api.get_payment_service")
def test_read_payment_success(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_payment_entity = PaymentEntity(
        id="123",
        order_id=1,
        amount=100.0,
        status="pending",
        qr_code="fake_qr",
        qr_code_expiration=3600,
    )
    mock_service.get_payment_by_id.return_value = mock_payment_entity

    payment_id = "123"
    response = read_payment(payment_id=payment_id, service=mock_service)

    mock_service.get_payment_by_id.assert_called_once_with(payment_id)
    assert response == serialize_payment(mock_payment_entity)


@patch("src.adapters.api.payment_api.get_payment_service")
def test_read_payment_not_found(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_service.get_payment_by_id.side_effect = EntityNotFound(
        "Payment not found"
    )

    payment_id = "123"
    with pytest.raises(Exception) as exc_info:
        read_payment(payment_id=payment_id, service=mock_service)

    mock_service.get_payment_by_id.assert_called_once_with(payment_id)
    assert exc_info.value.status_code == 404
    assert str(exc_info.value.detail) == "Payment not found"


@patch("src.adapters.api.payment_api.get_payment_service")
def test_update_payment_success(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_payment = PaymentUpdate(order_id=1, amount=200.0, status="completed")
    mock_payment_entity = PaymentEntity(
        id="123",
        order_id=1,
        amount=200.0,
        status="completed",
        qr_code="fake_qr",
        qr_code_expiration=3600,
    )
    mock_service.update_payment.return_value = mock_payment_entity

    payment_id = "123"
    response = update_payment(
        payment_id=payment_id, payment=mock_payment, service=mock_service
    )

    mock_service.update_payment.assert_called_once_with(
        payment_id=payment_id,
        order_id=mock_payment.order_id,
        amount=mock_payment.amount,
        status=mock_payment.status,
    )
    assert response == serialize_payment(mock_payment_entity)


@patch("src.adapters.api.payment_api.get_payment_service")
@pytest.mark.asyncio
async def test_handle_webhook_success(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_payment_entity = PaymentEntity(
        id="123",
        order_id=1,
        amount=100.0,
        status="pending",
        qr_code="fake_qr",
        qr_code_expiration=3600,
    )
    mock_service.handle_webhook.return_value = mock_payment_entity

    payload = WebhookPayload(payment_id="123", status="approved")
    response = await handle_webhook(payload=payload, service=mock_service)

    mock_service.handle_webhook.assert_called_once_with(
        payload.payment_id,
        payload.status,
    )
    assert response == serialize_payment(mock_payment_entity)


@patch("src.adapters.api.payment_api.get_payment_service")
def test_delete_payment_success(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    payment_id = "123"
    response = delete_payment(payment_id=payment_id, service=mock_service)

    mock_service.delete_payment.assert_called_once_with(payment_id)
    assert response == {"detail": "Payment deleted"}


@patch("src.adapters.api.payment_api.get_payment_service")
def test_delete_payment_not_found(mock_get_payment_service):
    mock_service = MagicMock(spec=PaymentService)
    mock_get_payment_service.return_value = mock_service

    mock_service.delete_payment.side_effect = EntityNotFound(
        "Payment not found"
    )

    payment_id = "123"
    with pytest.raises(Exception) as exc_info:
        delete_payment(payment_id=payment_id, service=mock_service)

    mock_service.delete_payment.assert_called_once_with(payment_id)
    assert exc_info.value.status_code == 404
    assert str(exc_info.value.detail) == "Payment not found"
