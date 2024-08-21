import logging
from typing import List, Optional

import aiohttp
from fastapi import HTTPException  # TODO remove this from service
from src.config import Config
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidEntity,
)
from src.domain.repositories.customer_repository import CustomerRepository
from src.domain.repositories.order_repository import OrderRepository
from src.infrastructure.messaging.inventory_publisher import InventoryPublisher
from src.infrastructure.messaging.order_update_publisher import (
    OrderUpdatePublisher,
)

logger = logging.getLogger("app")


class OrderService:

    def __init__(
        self,
        order_repository: OrderRepository,
        customer_repository: CustomerRepository,
        inventory_publisher: InventoryPublisher,  # TODO this should be a port
        order_update_publisher: OrderUpdatePublisher,  # TODO this should be a port
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.inventory_publisher = inventory_publisher
        self.order_update_publisher = order_update_publisher

    async def validate_inventory(
        self, order_items: List[OrderItemEntity]
    ) -> bool:
        async with aiohttp.ClientSession() as session:
            for item in order_items:
                url = f"{Config.INVENTORY_SERVICE_BASE_URL}/products/{item.product_sku}"
                logger.info(f"Validating invetory: {url}")
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(
                            f"Product SKU {item.product_sku} not found in inventory. "
                            f"Response: {response.status}, {await response.json()}"
                        )
                        return False
                    product = await response.json()
                    if product["quantity"] < item.quantity:
                        logger.error(
                            f"Insufficient quantity for SKU {item.product_sku}."
                        )
                        return False
        return True

    async def create_order(
        self, customer: CustomerEntity, order_items: List[OrderItemEntity]
    ) -> OrderEntity:
        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        # Validate inventory before creating the order
        if not await self.validate_inventory(order_items):
            raise HTTPException(
                status_code=400,
                detail=(
                    "One or more items in the order are not available "
                    "in the required quantity."
                ),
            )

        order = OrderEntity(
            customer=existing_customer,
            order_items=order_items,
        )

        try:
            for item in order_items:
                self.inventory_publisher.publish_inventory_update(
                    item.product_sku, "subtract", item.quantity
                )

            self.order_repository.save(order)
            order.total_amount = await self.calculate_order_total(order)
            return order

        except Exception as e:
            for item in order_items:
                self.inventory_publisher.publish_inventory_update(
                    item.product_sku, "add", item.quantity
                )
            raise e

    def get_order_by_id(self, order_id: int) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")
        return order

    def get_order_by_order_number(self, order_number: str) -> OrderEntity:
        order = self.order_repository.find_by_order_number(order_number)
        if not order:
            raise EntityNotFound(
                f"Order with Order Number '{order_number}' not found"
            )
        return order

    async def update_order(
        self,
        order_id: int,
        customer: CustomerEntity,
        order_items: List[OrderItemEntity],
    ) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        # Validate inventory before updating the order
        if not await self.validate_inventory(order_items):
            raise HTTPException(
                status_code=400,
                detail=(
                    "One or more items in the order are not available in "
                    "the required quantity."
                ),
            )

        inventory_changes = []

        try:
            current_order_items = {
                item.product_sku: item.quantity for item in order.order_items
            }

            for item in order_items:
                if item.product_sku in current_order_items:
                    old_quantity = current_order_items[item.product_sku]
                    if item.quantity > old_quantity:
                        diff = item.quantity - old_quantity
                        self.inventory_publisher.publish_inventory_update(
                            item.product_sku, "subtract", diff
                        )
                        inventory_changes.append((item.product_sku, diff))
                    elif item.quantity < old_quantity:
                        diff = old_quantity - item.quantity
                        self.inventory_publisher.publish_inventory_update(
                            item.product_sku, "add", diff
                        )
                        inventory_changes.append((item.product_sku, -diff))
                else:
                    self.inventory_publisher.publish_inventory_update(
                        item.product_sku,
                        "subtract",
                        item.quantity,
                    )
                    inventory_changes.append((item.product_sku, item.quantity))

            order.customer = existing_customer
            order.order_items = order_items
            self.order_repository.save(order)
            order.total_amount = await self.calculate_order_total(order)
            return order

        except Exception as e:
            for sku, quantity in inventory_changes:
                action = "add" if quantity > 0 else "subtract"
                self.inventory_publisher.publish_inventory_update(
                    sku, action, abs(quantity)
                )
            raise e

    def update_order_status(
        self, order_id: int, status: OrderStatus
    ) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        order.update_status(status)
        self.order_repository.save(order)
        return order

    def set_paid_order(self, order_id: int):
        """Sets the order status to PAID."""
        order = self.get_order_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")
        order.update_status(OrderStatus.PAID)
        self.order_repository.save(order)

    async def confirm_order(self, order_id: int) -> OrderEntity:
        order = self.get_order_by_id(order_id)
        if order.status != OrderStatus.PENDING:
            raise InvalidEntity("Only pending orders can be confirmed")

        order.update_status(OrderStatus.CONFIRMED)
        self.order_repository.save(order)
        try:
            order.total_amount = await self.calculate_order_total(order)
            self.order_update_publisher.publish_order_update(
                order_id=order.id,
                amount=order.total_amount,
                status=order.status.value,
            )
        except Exception as e:
            raise e
        return order

    def cancel_order(self, order_id: int) -> OrderEntity:
        order = self.get_order_by_id(order_id)
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise InvalidEntity(
                "Only pending or confirmed orders can be canceled"
            )

        for item in order.order_items:
            self.inventory_publisher.publish_inventory_update(
                item.product_sku, "add", item.quantity
            )

        order.update_status(OrderStatus.CANCELED)
        self.order_repository.save(order)
        try:
            self.order_update_publisher.publish_order_update(
                order_id=order.id, amount=0.0, status=order.status.value
            )
        except Exception as e:
            raise e
        return order

    def delete_order(self, order_id: int) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        self.order_repository.delete(order)
        return order

    def list_orders(self) -> List[OrderEntity]:
        return self.order_repository.list_all()

    async def calculate_order_total(self, order: OrderEntity) -> float:
        total_amount = 0.0
        async with aiohttp.ClientSession() as session:
            for item in order.order_items:
                async with session.get(
                    f"{Config.INVENTORY_SERVICE_BASE_URL}/products/{item.product_sku}"
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Product {item.product_sku} not found",
                        )
                    product = await response.json()
                    total_amount += product["price"] * item.quantity
        return total_amount

    def get_all_customers(self) -> List[CustomerEntity]:
        return self.customer_repository.list_all()

    def get_customer_by_email(self, email: str) -> Optional[CustomerEntity]:
        return self.customer_repository.find_by_email(email)

    def create_customer(self, customer: CustomerEntity) -> CustomerEntity:
        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if existing_customer:
            raise EntityAlreadyExists(
                f"Customer with email '{customer.email}' already exists."
            )

        self.customer_repository.save(customer)
        return customer

    def update_customer(
        self, email: str, updated_customer: CustomerEntity
    ) -> CustomerEntity:
        customer = self.customer_repository.find_by_email(email)
        if not customer:
            raise EntityNotFound(f"Customer with email '{email}' not found")

        customer.name = updated_customer.name
        customer.email = updated_customer.email
        customer.phone_number = updated_customer.phone_number
        self.customer_repository.save(customer)
        # TODO should get from repository again, not return the argument
        return customer

    def delete_customer(self, email: str) -> None:
        customer = self.customer_repository.find_by_email(email)
        if not customer:
            raise EntityNotFound(f"Customer with email '{email}' not found")

        self.customer_repository.delete(customer)
