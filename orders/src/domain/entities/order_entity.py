import uuid
from enum import Enum
from typing import List, Optional

from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_item_entity import OrderItemEntity


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"
    PAID = "paid"


class OrderEntity:

    def __init__(
        self,
        customer: CustomerEntity,
        order_items: List[OrderItemEntity],
        status: OrderStatus = OrderStatus.PENDING,
        id: Optional[int] = None,
        order_number: Optional[str] = None,
        total_amount: Optional[float] = None,
    ):
        self.id = id
        self.order_number = order_number or str(uuid.uuid4())
        self.customer = customer
        self.order_items = order_items
        self.status = status
        self.total_amount = total_amount or 0.0

    def add_item(self, order_item: OrderItemEntity):
        self.order_items.append(order_item)

    def update_status(self, new_status: OrderStatus):
        self.status = new_status
