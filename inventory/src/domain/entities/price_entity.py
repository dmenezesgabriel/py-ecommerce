from typing import Optional

from src.domain.exceptions import InvalidEntity


class PriceEntity:
    def __init__(self, amount: float, id: Optional[int] = None):
        self._id = id
        self._amount = amount

        # Validate attributes during initialization
        self._validate_id(self._id)
        self._validate_amount(self._amount)

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        self._validate_id(value)
        self._id = value

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float):
        self._validate_amount(value)
        self._amount = value

    def _validate_id(self, id_value: Optional[int]):
        if id_value is not None and (
            not isinstance(id_value, int) or id_value <= 0
        ):
            raise InvalidEntity(
                f"Invalid id: {id_value}. ID must be a positive integer or None."
            )

    def _validate_amount(self, amount_value: float):
        if not isinstance(amount_value, (int, float)) or amount_value < 0:
            raise InvalidEntity(
                f"Invalid amount: {amount_value}. Amount must be a non-negative number."
            )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "amount": self._amount,
        }
