from typing import Optional


class OrderItemEntity:
    def __init__(
        self, product_sku: str, quantity: int, id: Optional[int] = None
    ):
        self.id = id
        self.product_sku = product_sku
        self.quantity = quantity
