from enum import Enum
from typing import Optional

from src.domain.exceptions import InvalidEntity


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
        self._id = id
        self._order_id = order_id
        self._amount = amount
        self._status = status
        self._qr_code = qr_code
        self._qr_code_expiration = qr_code_expiration

        # Validate attributes during initialization
        self._validate_id(self._id)
        self._validate_order_id(self._order_id)
        self._validate_amount(self._amount)
        self._validate_status(self._status)
        self._validate_qr_code_expiration(self._qr_code_expiration)

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]):
        self._validate_id(value)
        self._id = value

    @property
    def order_id(self) -> int:
        return self._order_id

    @order_id.setter
    def order_id(self, value: int):
        self._validate_order_id(value)
        self._order_id = value

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float):
        self._validate_amount(value)
        self._amount = value

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self._validate_status(value)
        self._status = value

    @property
    def qr_code(self) -> Optional[str]:
        return self._qr_code

    @qr_code.setter
    def qr_code(self, value: Optional[str]):
        self._qr_code = value

    @property
    def qr_code_expiration(self) -> Optional[int]:
        return self._qr_code_expiration

    @qr_code_expiration.setter
    def qr_code_expiration(self, value: Optional[int]):
        self._validate_qr_code_expiration(value)
        self._qr_code_expiration = value

    def update_status(self, new_status: str):
        self.status = new_status

    def _validate_id(self, id_value: Optional[str]):
        if id_value is not None and not isinstance(id_value, str):
            raise InvalidEntity(
                f"Invalid id: {id_value}. " "ID must be a string or None."
            )

    def _validate_order_id(self, order_id_value: int):
        if not isinstance(order_id_value, int) or order_id_value <= 0:
            raise InvalidEntity(
                f"Invalid order_id: {order_id_value}. "
                "Order ID must be a positive integer."
            )

    def _validate_amount(self, amount_value: float):
        if not isinstance(amount_value, float) or amount_value <= 0:
            raise InvalidEntity(
                f"Invalid amount: {amount_value}. "
                "Amount must be a positive float."
            )

    def _validate_status(self, status_value: str):
        if status_value not in PaymentStatus.__members__.values():
            raise InvalidEntity(
                f"Invalid status: {status_value}. "
                "Status must be one of the valid PaymentStatus values."
            )

    def _validate_qr_code_expiration(self, expiration_value: Optional[int]):
        if expiration_value is not None and (
            not isinstance(expiration_value, int) or expiration_value <= 0
        ):
            raise InvalidEntity(
                f"Invalid qr_code_expiration: {expiration_value}. "
                "QR Code expiration must be a positive integer or None."
            )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "order_id": self._order_id,
            "amount": self._amount,
            "status": self._status,
            "qr_code": self._qr_code,
            "qr_code_expiration": self._qr_code_expiration,
        }
