from src.application.dto.payment_dto import PaymentResponse
from src.domain.entities.payment_entity import PaymentEntity


def serialize_payment(payment: PaymentEntity) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        status=payment.status,
        qr_code=payment.qr_code,
        qr_code_expiration=payment.qr_code_expiration,
    )
