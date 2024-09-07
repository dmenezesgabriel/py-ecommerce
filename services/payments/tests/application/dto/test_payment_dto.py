import pytest
from pydantic import ValidationError
from src.application.dto.payment_dto import (
    PaymentCreate,
    PaymentResponse,
    PaymentStatusUpdate,
    PaymentUpdate,
    WebhookPayload,
)
from src.domain.entities.payment_entity import PaymentStatus


def test_payment_create_valid():
    dto = PaymentCreate(
        order_id=1, amount=100.00, status=PaymentStatus.PENDING
    )
    assert dto.order_id == 1
    assert dto.amount == 100.00
    assert dto.status == PaymentStatus.PENDING


def test_payment_create_invalid():
    with pytest.raises(ValidationError):
        PaymentCreate(order_id=-1, amount=-100.00, status="invalid_status")


def test_payment_update_valid():
    dto = PaymentUpdate(
        order_id=1, amount=150.00, status=PaymentStatus.COMPLETED
    )
    assert dto.order_id == 1
    assert dto.amount == 150.00
    assert dto.status == PaymentStatus.COMPLETED


def test_payment_update_invalid():
    with pytest.raises(ValidationError):
        PaymentUpdate(
            order_id="invalid_order_id",
            amount="invalid_amount",
            status="invalid_status",
        )


def test_payment_status_update_valid():
    dto = PaymentStatusUpdate(status=PaymentStatus.REFUNDED)
    assert dto.status == PaymentStatus.REFUNDED


def test_payment_status_update_invalid():
    with pytest.raises(ValidationError):
        PaymentStatusUpdate(status="invalid_status")


def test_payment_response_valid():
    dto = PaymentResponse(
        id="64c8cbe2f3a5e9a1c4b63e29",
        order_id=1,
        amount=100.00,
        status=PaymentStatus.COMPLETED,
        qr_code="https://www.mercadopago.com.br/qr-code/1",
        qr_code_expiration=1633520400,
    )
    assert dto.id == "64c8cbe2f3a5e9a1c4b63e29"
    assert dto.order_id == 1
    assert dto.amount == 100.00
    assert dto.status == PaymentStatus.COMPLETED
    assert dto.qr_code == "https://www.mercadopago.com.br/qr-code/1"
    assert dto.qr_code_expiration == 1633520400


def test_payment_response_invalid():
    with pytest.raises(ValidationError):
        PaymentResponse(
            id=123,  # Invalid ID, should be a string
            order_id="invalid_order_id",  # Invalid order ID, should be an int
            amount="invalid_amount",  # Invalid amount, should be a float
            status="invalid_status",  # Invalid status
        )


def test_webhook_payload_valid():
    dto = WebhookPayload(
        payment_id="64c8cbe2f3a5e9a1c4b63e29", status="approved"
    )
    assert dto.payment_id == "64c8cbe2f3a5e9a1c4b63e29"
    assert dto.status == "approved"


def test_webhook_payload_invalid():
    with pytest.raises(ValidationError):
        WebhookPayload(
            payment_id=12345, status=None
        )  # Invalid payment ID and status


def test_payment_create_examples():
    examples = PaymentCreate.model_config["json_schema_extra"]["examples"]
    for example in examples:
        dto = PaymentCreate(**example)
        assert dto.order_id == example["order_id"]
        assert dto.amount == example["amount"]
        assert dto.status == PaymentStatus(example["status"])


def test_payment_update_examples():
    examples = PaymentUpdate.model_config["json_schema_extra"]["examples"]
    for example in examples:
        dto = PaymentUpdate(**example)
        assert dto.order_id == example["order_id"]
        assert dto.amount == example["amount"]
        assert dto.status == PaymentStatus(example["status"])


def test_payment_status_update_examples():
    examples = PaymentStatusUpdate.model_config["json_schema_extra"][
        "examples"
    ]
    for example in examples:
        dto = PaymentStatusUpdate(**example)
        assert dto.status == PaymentStatus(example["status"])


def test_payment_response_examples():
    examples = PaymentResponse.model_config["json_schema_extra"]["examples"]
    for example in examples:
        dto = PaymentResponse(**example)
        assert dto.id == example["id"]
        assert dto.order_id == example["order_id"]
        assert dto.amount == example["amount"]
        assert dto.status == PaymentStatus(example["status"])
        assert dto.qr_code == example.get("qr_code")
        assert dto.qr_code_expiration == example.get("qr_code_expiration")


def test_webhook_payload_examples():
    examples = WebhookPayload.model_config["json_schema_extra"]["examples"]
    for example in examples:
        dto = WebhookPayload(**example)
        assert dto.payment_id == example["payment_id"]
        assert dto.status == example["status"]
