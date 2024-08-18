from typing import Optional


class InventoryEntity:
    def __init__(self, quantity: int, id: Optional[int] = None):
        self.id = id
        self.quantity = quantity

    def set_quantity(self, amount: int):
        self.quantity = amount
