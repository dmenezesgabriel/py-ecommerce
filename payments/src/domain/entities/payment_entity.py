from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class PaymentEntity:
    def __init__(
        self,
        order_id: int,
        amount: float,
        status: str,
        qr_code: Optional[str] = None,
        qr_code_expiration: Optional[int] = None,
        id: Optional[str] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.status = status
        self.qr_code = qr_code
        self.qr_code_expiration = qr_code_expiration

    def update_status(self, new_status: str):
        self.status = new_status
