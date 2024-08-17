from enum import Enum
from typing import Optional

from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class DeliveryEntity:
    def __init__(
        self,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
        id: Optional[int] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.delivery_address = delivery_address
        self.delivery_date = delivery_date
        self.status = status
        self.customer = customer
        self.address = address

    def update_status(self, new_status: DeliveryStatus):
        self.status = new_status
