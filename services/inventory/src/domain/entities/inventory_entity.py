from typing import Optional

from src.domain.exceptions import InvalidEntity


class InventoryEntity:
    def __init__(self, quantity: int, id: Optional[int] = None):
        self._id = id
        self._quantity = quantity

        # Validate attributes during initialization
        self._validate_id(self._id)
        self._validate_quantity(self._quantity)

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        self._validate_id(value)
        self._id = value

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        self._validate_quantity(value)
        self._quantity = value

    def set_quantity(self, amount: int):
        self.quantity = amount

    def _validate_id(self, id_value: Optional[int]):
        if id_value is not None and (
            not isinstance(id_value, int) or id_value <= 0
        ):
            raise InvalidEntity(
                f"Invalid id: {id_value}. "
                "ID must be a positive integer or None."
            )

    def _validate_quantity(self, quantity_value: int):
        if not isinstance(quantity_value, int) or quantity_value < 0:
            raise InvalidEntity(
                f"Invalid quantity: {quantity_value}. "
                "Quantity must be a non-negative integer."
            )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "quantity": self._quantity,
        }
