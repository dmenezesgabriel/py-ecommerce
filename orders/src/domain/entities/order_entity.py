import uuid
from enum import Enum
from typing import List, Optional

from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import InvalidEntity


class OrderStatus(Enum):
    PENDING = "pending"
    RECEIVED = "received"
    PREPARING = "preparing"
    READY = "ready"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    FINISHED = "finished"
    CANCELED = "canceled"
    PAID = "paid"


class OrderEntity:

    def __init__(
        self,
        customer: CustomerEntity,
        order_items: List[OrderItemEntity],
        status: OrderStatus = OrderStatus.PENDING,
        estimated_time: Optional[str] = None,
        id: Optional[int] = None,
        order_number: Optional[str] = None,
        total_amount: Optional[float] = None,
    ):
        self._id = id
        self._order_number = order_number or str(uuid.uuid4())
        self._customer = customer
        self._order_items = order_items
        self._status = status
        self._total_amount = total_amount or 0.0
        self._estimated_time = estimated_time

        self._validate_id(self._id)
        self._validate_order_number(self._order_number)
        self._validate_customer(self._customer)
        self._validate_order_items(self._order_items)
        self._validate_total_amount(self._total_amount)
        self._validate_estimated_time(self._estimated_time)

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        self._validate_id(value)
        self._id = value

    @property
    def order_number(self) -> str:
        return self._order_number

    @order_number.setter
    def order_number(self, value: str):
        self._validate_order_number(value)
        self._order_number = value

    @property
    def customer(self) -> CustomerEntity:
        return self._customer

    @customer.setter
    def customer(self, value: CustomerEntity):
        self._validate_customer(value)
        self._customer = value

    @property
    def order_items(self) -> List[OrderItemEntity]:
        return self._order_items

    @order_items.setter
    def order_items(self, value: List[OrderItemEntity]):
        self._validate_order_items(value)
        self._order_items = value

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, value: OrderStatus):
        self._status = value

    @property
    def total_amount(self) -> float:
        return self._total_amount

    @total_amount.setter
    def total_amount(self, value: float):
        self._validate_total_amount(value)
        self._total_amount = value

    @property
    def estimated_time(self) -> Optional[str]:
        return self._estimated_time

    @estimated_time.setter
    def estimated_time(self, value: Optional[str]):
        self._validate_estimated_time(value)
        self._estimated_time = value

    def add_item(self, order_item: OrderItemEntity):
        self._order_items.append(order_item)

    def update_status(self, new_status: OrderStatus):
        self._status = new_status

    def _validate_id(self, id_value: Optional[int]):
        if id_value is not None and (
            not isinstance(id_value, int) or id_value <= 0
        ):
            raise InvalidEntity(
                f"Invalid id: {id_value}. ID must be a positive integer or None."
            )

    def _validate_order_number(self, order_number_value: str):
        if (
            not isinstance(order_number_value, str)
            or not order_number_value.strip()
        ):
            raise InvalidEntity(
                f"Invalid order number: {order_number_value}. Order number must be a non-empty string."
            )

    def _validate_customer(self, customer_value: CustomerEntity):
        if not isinstance(customer_value, CustomerEntity):
            raise InvalidEntity(
                "Invalid customer. Must be a CustomerEntity instance."
            )

    def _validate_order_items(self, order_items_value: List[OrderItemEntity]):
        if not isinstance(order_items_value, list) or not all(
            isinstance(item, OrderItemEntity) for item in order_items_value
        ):
            raise InvalidEntity(
                "Invalid order items. Must be a list of OrderItemEntity instances."
            )

    def _validate_total_amount(self, total_amount_value: float):
        if (
            not isinstance(total_amount_value, (int, float))
            or total_amount_value < 0
        ):
            raise InvalidEntity(
                f"Invalid total amount: {total_amount_value}. Total amount must be a non-negative number."
            )

    def _validate_estimated_time(self, estimated_time_value: Optional[str]):
        if estimated_time_value is not None and not isinstance(
            estimated_time_value, str
        ):
            raise InvalidEntity(
                f"Invalid estimated time: {estimated_time_value}. Must be a valid string."
            )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "order_number": self._order_number,
            "customer": self._customer.to_dict(),
            "order_items": [item.to_dict() for item in self._order_items],
            "status": self._status.value,
            "total_amount": self._total_amount,
            "estimated_time": self._estimated_time,
        }
