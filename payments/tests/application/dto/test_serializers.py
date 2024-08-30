from unittest.mock import MagicMock

from src.application.dto.payment_dto import PaymentResponse
from src.application.dto.serializers import serialize_payment
from src.domain.entities.payment_entity import PaymentEntity


def test_serialize_payment():
    # Create a mock PaymentEntity
    payment_entity_mock = MagicMock(spec=PaymentEntity)

    # Define the attributes of the mock PaymentEntity
    payment_entity_mock.id = "64c8cbe2f3a5e9a1c4b63e29"
    payment_entity_mock.order_id = 1
    payment_entity_mock.amount = 100.00
    payment_entity_mock.status = "completed"
    payment_entity_mock.qr_code = "https://www.mercadopago.com.br/qr-code/1"
    payment_entity_mock.qr_code_expiration = 1633520400

    # Call the serialize_payment function
    serialized_payment = serialize_payment(payment_entity_mock)

    # Verify the returned PaymentResponse matches the expected data
    assert isinstance(serialized_payment, PaymentResponse)
    assert serialized_payment.id == payment_entity_mock.id
    assert serialized_payment.order_id == payment_entity_mock.order_id
    assert serialized_payment.amount == payment_entity_mock.amount
    assert serialized_payment.status == payment_entity_mock.status
    assert serialized_payment.qr_code == payment_entity_mock.qr_code
    assert (
        serialized_payment.qr_code_expiration
        == payment_entity_mock.qr_code_expiration
    )
