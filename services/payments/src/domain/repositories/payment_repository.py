from typing import Optional

from src.domain.entities.payment_entity import PaymentEntity


class PaymentRepository:
    def save(self, payment: PaymentEntity):
        raise NotImplementedError

    def find_by_id(self, payment_id: str) -> Optional[PaymentEntity]:
        raise NotImplementedError

    def find_by_order_id(self, order_id: int) -> Optional[PaymentEntity]:
        raise NotImplementedError

    def delete(self, payment: PaymentEntity):
        raise NotImplementedError
