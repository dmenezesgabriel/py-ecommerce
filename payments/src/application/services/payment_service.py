from src.domain.entities.payment_entity import PaymentEntity, PaymentStatus
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidAction,
)


class PaymentService:
    def __init__(self, payment_repository, payment_publisher, qr_code_service):
        self.payment_repository = payment_repository
        self.payment_publisher = payment_publisher
        self.qr_code_service = qr_code_service

    def create_payment(
        self, order_id: int, amount: float, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_order_id(order_id)
        if payment:
            raise EntityAlreadyExists(
                f"Payment with order_id '{order_id}' already exists"
            )

        qr_code, qr_code_expiration = self.qr_code_service.create_qr_code(
            order_id, amount
        )

        payment_entity = PaymentEntity(
            order_id=order_id,
            amount=amount,
            status=status,
            qr_code=qr_code,
            qr_code_expiration=qr_code_expiration,
        )
        self.payment_repository.save(payment_entity)
        return payment_entity

    def get_payment_by_id(self, payment_id: str) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")
        return payment

    def get_payment_by_order_id(self, order_id: int) -> PaymentEntity:
        payment = self.payment_repository.find_by_order_id(order_id)
        if not payment:
            raise EntityNotFound(
                f"Payment with order_id '{order_id}' not found"
            )
        return payment

    def update_payment(
        self, payment_id: str, order_id: int, amount: float, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        if payment.status == PaymentStatus.CANCELED.value:
            raise InvalidAction("Cannot modify a canceled payment")

        payment.order_id = order_id
        payment.amount = amount
        payment.status = status
        self.payment_repository.save(payment)
        return payment

    def update_payment_status(
        self, payment_id: str, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        if payment.status == PaymentStatus.CANCELED.value:
            raise InvalidAction(
                "Cannot change the status of a canceled payment"
            )

        if (
            status
            in [
                PaymentStatus.COMPLETED.value,
                PaymentStatus.FAILED.value,
                PaymentStatus.REFUNDED.value,
            ]
            and payment.status == PaymentStatus.CANCELED.value
        ):
            raise InvalidAction(
                f"Cannot {status.lower()} a payment that has been canceled"
            )

        payment.update_status(status)
        self.payment_repository.save(payment)

        # Publish the status update
        self.payment_publisher.publish_payment_update(
            payment_id=payment.id,
            order_id=payment.order_id,
            status=payment.status,
        )

        return payment

    def cancel_payment(self, payment_id: str) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        if payment.status in [
            PaymentStatus.COMPLETED.value,
            PaymentStatus.FAILED.value,
            PaymentStatus.REFUNDED.value,
            PaymentStatus.CANCELED.value,
        ]:
            raise InvalidAction(
                """
                Cannot cancel a payment that has been completed,
                 failed, refunded, or already canceled
                """
            )

        payment.update_status(PaymentStatus.CANCELED.value)
        self.payment_repository.save(payment)

        # Publish the status update
        self.payment_publisher.publish_payment_update(
            payment_id=payment.id,
            order_id=payment.order_id,
            status=payment.status,
        )

        return payment

    def delete_payment(self, payment_id: str):
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        self.payment_repository.delete(payment)
        return payment

    def handle_webhook(self, payment_id: str, status: str) -> PaymentEntity:
        payment = self.get_payment_by_id(payment_id)
        if status == "approved":
            updated_payment = self.update_payment_status(
                payment.id, PaymentStatus.COMPLETED.value
            )
        elif status == "rejected":
            updated_payment = self.update_payment_status(
                payment.id, PaymentStatus.FAILED.value
            )
        else:
            raise InvalidAction(f"Unsupported status '{status}' in webhook")

        return updated_payment
