from datetime import datetime
from enum import Enum
from typing import Optional

from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.exceptions import InvalidEntity


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

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        if value is not None and value <= 0:
            raise InvalidEntity("ID must be a positive integer.")
        self._id = value

    @property
    def order_id(self) -> int:
        return self._order_id

    @order_id.setter
    def order_id(self, value: int):
        if value <= 0:
            raise InvalidEntity("Order ID must be a positive integer.")
        self._order_id = value

    @property
    def delivery_address(self) -> str:
        return self._delivery_address

    @delivery_address.setter
    def delivery_address(self, value: str):
        if not value or len(value) < 5:
            raise InvalidEntity(
                "Delivery address must be at least 5 characters long."
            )
        self._delivery_address = value

    @property
    def delivery_date(self) -> str:
        return self._delivery_date

    @delivery_date.setter
    def delivery_date(self, value: str):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise InvalidEntity(
                "Delivery date must be in the format YYYY-MM-DD."
            )
        self._delivery_date = value

    @property
    def status(self) -> DeliveryStatus:
        return self._status

    @status.setter
    def status(self, value: str):
        try:
            self._status = DeliveryStatus(value)
        except ValueError:
            raise InvalidEntity("Invalid delivery status.")

    @property
    def customer(self) -> CustomerEntity:
        return self._customer

    @customer.setter
    def customer(self, value: CustomerEntity):
        if not isinstance(value, CustomerEntity):
            raise InvalidEntity("Invalid customer information.")
        self._customer = value

    @property
    def address(self) -> AddressEntity:
        return self._address

    @address.setter
    def address(self, value: AddressEntity):
        if not isinstance(value, AddressEntity):
            raise InvalidEntity("Invalid address information.")
        self._address = value

    def update_status(self, new_status: DeliveryStatus):
        self.status = new_status
