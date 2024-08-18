from typing import Optional


class PriceEntity:
    def __init__(self, amount: float, id: Optional[int] = None):
        self.id = id
        self.amount = amount
