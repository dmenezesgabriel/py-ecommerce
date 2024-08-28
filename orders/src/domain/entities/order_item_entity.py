from typing import Optional

from src.domain.exceptions import InvalidEntity


class OrderItemEntity:

    def __init__(
        self,
        product_sku: str,
        quantity: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        id: Optional[int] = None,
    ):
        self._id = id
        self._product_sku = product_sku
        self._quantity = quantity
        self._name = name
        self._description = description
        self._price = price

        # Validate attributes during initialization
        self._validate_id(self._id)
        self._validate_product_sku(self._product_sku)
        self._validate_quantity(self._quantity)

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        self._validate_id(value)
        self._id = value

    @property
    def product_sku(self) -> str:
        return self._product_sku

    @product_sku.setter
    def product_sku(self, value: str):
        self._validate_product_sku(value)
        self._product_sku = value

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        self._validate_quantity(value)
        self._quantity = value

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Optional[str]):
        self._name = value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        self._description = value

    @property
    def price(self) -> Optional[float]:
        return self._price

    @price.setter
    def price(self, value: Optional[float]):
        self._price = value

    def _validate_id(self, id_value: Optional[int]):
        if id_value is not None and (
            not isinstance(id_value, int) or id_value <= 0
        ):
            raise InvalidEntity(
                f"Invalid id: {id_value}. "
                "ID must be a positive integer or None."
            )

    def _validate_product_sku(self, product_sku_value: str):
        if (
            not isinstance(product_sku_value, str)
            or not product_sku_value.strip()
        ):
            raise InvalidEntity(
                f"Invalid product SKU: {product_sku_value}. "
                "SKU must be a non-empty string."
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
            "product_sku": self._product_sku,
            "quantity": self._quantity,
            "name": self._name,
            "description": self._description,
            "price": self._price,
        }
