from typing import Optional

from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.inventory_entity import InventoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.exceptions import InvalidEntity


class ProductEntity:
    def __init__(
        self,
        sku: str,
        name: str,
        category: CategoryEntity,
        price: PriceEntity,
        inventory: InventoryEntity,
        id: Optional[int] = None,
    ):
        self.id = id
        self.sku = sku
        self.name = name
        self.category = category
        self.price = price
        self.inventory = inventory

    def set_inventory(self, quantity: int):
        self.inventory.set_quantity(quantity)

    def set_price(self, amount: float):
        self.price.amount = amount

    def add_inventory(self, quantity: int):
        if quantity < 0:
            raise InvalidEntity("Quantity to add must be positive.")
        self.inventory.quantity += quantity

    def subtract_inventory(self, quantity: int):
        if quantity < 0:
            raise InvalidEntity("Quantity to subtract must be positive.")
        if self.inventory.quantity < quantity:
            raise InvalidEntity(
                f"Cannot subtract {quantity} items. Only {self.inventory.quantity} available."
            )
        self.inventory.quantity -= quantity
