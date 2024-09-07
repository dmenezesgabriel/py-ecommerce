from typing import List, Optional

from src.application.services.order_verification_service import (
    OrderVerificationService,
)
from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity, DeliveryStatus
from src.domain.exceptions import EntityNotFound, InvalidOperation
from src.domain.repositories.customer_repository import CustomerRepository
from src.domain.repositories.delivery_repository import DeliveryRepository
from src.infrastructure.messaging.delivery_publisher import DeliveryPublisher


class DeliveryService:
    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        customer_repository: CustomerRepository,
        delivery_publisher: DeliveryPublisher,
        order_verification_service: OrderVerificationService,
    ):
        self.delivery_repository = delivery_repository
        self.customer_repository = customer_repository
        self.delivery_publisher = delivery_publisher
        self.order_verification_service = order_verification_service

    async def create_delivery(
        self,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
    ) -> DeliveryEntity:
        order_exists = await self.order_verification_service.verify_order(
            order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{order_id}' does not exist or is canceled"
            )

        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        delivery = DeliveryEntity(
            order_id=order_id,
            delivery_address=delivery_address,
            delivery_date=delivery_date,
            status=status,
            customer=existing_customer,
            address=address,
        )
        self.delivery_repository.save(delivery)
        return delivery

    def get_delivery_by_id(self, delivery_id: int) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")
        return delivery

    async def get_delivery_by_order_id(self, order_id: int) -> DeliveryEntity:
        order_exists = await self.order_verification_service.verify_order(
            order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{order_id}' does not exist or is canceled"
            )

        delivery = self.delivery_repository.find_by_order_id(order_id)
        if not delivery:
            raise EntityNotFound(
                f"Delivery with Order ID '{order_id}' not found"
            )
        return delivery

    async def update_delivery(
        self,
        delivery_id: int,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
    ) -> DeliveryEntity:
        order_exists = await self.order_verification_service.verify_order(
            order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{order_id}' does not exist or is canceled"
            )

        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        delivery.order_id = order_id
        delivery.delivery_address = delivery_address
        delivery.delivery_date = delivery_date
        delivery.status = status
        delivery.customer = existing_customer
        delivery.address = address

        self.delivery_repository.save(delivery)
        return delivery

    async def update_delivery_status(
        self, delivery_id: int, status: DeliveryStatus
    ) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        order_exists = await self.order_verification_service.verify_order(
            delivery.order_id
        )
        if not order_exists:
            message = f"""
            Order with ID '{delivery.order_id}' does not exist or is canceled
            """
            raise InvalidOperation(message)

        delivery.update_status(status)
        self.delivery_repository.save(delivery)

        # Publish the delivery status update
        self.delivery_publisher.publish_delivery_update(
            delivery_id=delivery.id,
            order_id=delivery.order_id,
            status=delivery.status.value,
        )

        return delivery

    async def delete_delivery(self, delivery_id: int) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        order_exists = await self.order_verification_service.verify_order(
            delivery.order_id
        )
        if not order_exists:
            message = f"""
            Order with ID '{delivery.order_id}' does not exist or is canceled
            """
            raise InvalidOperation(message)

        self.delivery_repository.delete(delivery)
        return delivery

    def list_deliveries(self) -> List[DeliveryEntity]:
        return self.delivery_repository.list_all()

    def get_customer_by_email(self, email: str) -> Optional[CustomerEntity]:
        return self.customer_repository.find_by_email(email)

    def list_customers(self) -> List[CustomerEntity]:
        return self.customer_repository.list_all()

    def save_customer(self, customer: CustomerEntity):
        self.customer_repository.save(customer)

    def delete_customer(self, customer: CustomerEntity):
        self.customer_repository.delete(customer)
