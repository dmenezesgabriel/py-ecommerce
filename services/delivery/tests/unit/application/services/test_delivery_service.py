import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.services.delivery_service import DeliveryService
from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity, DeliveryStatus
from src.domain.exceptions import EntityNotFound, InvalidOperation


class TestDeliveryService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Arrange common test data
        self.mock_delivery_repository = MagicMock()
        self.mock_customer_repository = MagicMock()
        self.mock_delivery_publisher = MagicMock()
        self.mock_order_verification_service = MagicMock()

        self.delivery_service = DeliveryService(
            delivery_repository=self.mock_delivery_repository,
            customer_repository=self.mock_customer_repository,
            delivery_publisher=self.mock_delivery_publisher,
            order_verification_service=self.mock_order_verification_service,
        )

        self.customer = CustomerEntity(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
        )
        self.address = AddressEntity(
            id=1,
            city="New York",
            state="NY",
            country="USA",
            zip_code="10001",
        )
        self.delivery = DeliveryEntity(
            id=1,
            order_id=123,
            delivery_address="123 Main St, Apt 4B",
            delivery_date="2024-08-20",
            status=DeliveryStatus.PENDING,
            customer=self.customer,
            address=self.address,
        )

    @patch("src.application.services.delivery_service.DeliveryEntity")
    async def test_create_delivery_success(self, MockDeliveryEntity):
        # Arrange
        self.mock_order_verification_service.verify_order = AsyncMock(return_value=True)
        self.mock_customer_repository.find_by_email.return_value = None
        MockDeliveryEntity.return_value = self.delivery

        # Act
        delivery = await self.delivery_service.create_delivery(
            order_id=self.delivery.order_id,
            delivery_address=self.delivery.delivery_address,
            delivery_date=self.delivery.delivery_date,
            status=self.delivery.status,
            customer=self.customer,
            address=self.address,
        )

        # Assert
        self.mock_order_verification_service.verify_order.assert_called_once_with(
            self.delivery.order_id
        )
        self.mock_customer_repository.find_by_email.assert_called_once_with(
            self.customer.email
        )
        self.mock_customer_repository.save.assert_called_once_with(self.customer)
        self.mock_delivery_repository.save.assert_called_once_with(self.delivery)
        self.assertEqual(delivery, self.delivery)

    async def test_create_delivery_order_not_found(self):
        # Arrange
        self.mock_order_verification_service.verify_order = AsyncMock(
            return_value=False
        )

        # Act & Assert
        with self.assertRaises(InvalidOperation):
            await self.delivery_service.create_delivery(
                order_id=self.delivery.order_id,
                delivery_address=self.delivery.delivery_address,
                delivery_date=self.delivery.delivery_date,
                status=self.delivery.status,
                customer=self.customer,
                address=self.address,
            )

    def test_get_delivery_by_id_success(self):
        # Arrange
        self.mock_delivery_repository.find_by_id.return_value = self.delivery

        # Act
        delivery = self.delivery_service.get_delivery_by_id(self.delivery.id)

        # Assert
        self.mock_delivery_repository.find_by_id.assert_called_once_with(
            self.delivery.id
        )
        self.assertEqual(delivery, self.delivery)

    def test_get_delivery_by_id_not_found(self):
        # Arrange
        self.mock_delivery_repository.find_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(EntityNotFound):
            self.delivery_service.get_delivery_by_id(self.delivery.id)

    @patch("src.application.services.delivery_service.DeliveryEntity")
    async def test_update_delivery_success(self, MockDeliveryEntity):
        # Arrange
        self.mock_order_verification_service.verify_order = AsyncMock(return_value=True)
        self.mock_delivery_repository.find_by_id.return_value = self.delivery
        self.mock_customer_repository.find_by_email.return_value = self.customer

        # Act
        updated_delivery = await self.delivery_service.update_delivery(
            delivery_id=self.delivery.id,
            order_id=self.delivery.order_id,
            delivery_address=self.delivery.delivery_address,
            delivery_date=self.delivery.delivery_date,
            status=self.delivery.status,
            customer=self.customer,
            address=self.address,
        )

        # Assert
        self.mock_order_verification_service.verify_order.assert_called_once_with(
            self.delivery.order_id
        )
        self.mock_delivery_repository.find_by_id.assert_called_once_with(
            self.delivery.id
        )
        self.mock_customer_repository.find_by_email.assert_called_once_with(
            self.customer.email
        )
        self.mock_delivery_repository.save.assert_called_once_with(self.delivery)
        self.assertEqual(updated_delivery, self.delivery)

    async def test_update_delivery_order_not_found(self):
        # Arrange
        self.mock_order_verification_service.verify_order = AsyncMock(
            return_value=False
        )

        # Act & Assert
        with self.assertRaises(InvalidOperation):
            await self.delivery_service.update_delivery(
                delivery_id=self.delivery.id,
                order_id=self.delivery.order_id,
                delivery_address=self.delivery.delivery_address,
                delivery_date=self.delivery.delivery_date,
                status=self.delivery.status,
                customer=self.customer,
                address=self.address,
            )

    async def test_update_delivery_status_success(self):
        # Arrange
        self.mock_delivery_repository.find_by_id.return_value = self.delivery
        self.mock_order_verification_service.verify_order = AsyncMock(return_value=True)

        # Act
        updated_delivery = await self.delivery_service.update_delivery_status(
            delivery_id=self.delivery.id,
            status=DeliveryStatus.IN_TRANSIT,
        )

        # Assert
        self.mock_delivery_repository.find_by_id.assert_called_once_with(
            self.delivery.id
        )
        self.mock_order_verification_service.verify_order.assert_called_once_with(
            self.delivery.order_id
        )
        self.mock_delivery_repository.save.assert_called_once_with(self.delivery)
        self.mock_delivery_publisher.publish_delivery_update.assert_called_once_with(
            delivery_id=self.delivery.id,
            order_id=self.delivery.order_id,
            status=DeliveryStatus.IN_TRANSIT.value,
        )
        self.assertEqual(updated_delivery.status, DeliveryStatus.IN_TRANSIT)

    async def test_update_delivery_status_delivery_not_found(self):
        # Arrange
        self.mock_delivery_repository.find_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(EntityNotFound):
            await self.delivery_service.update_delivery_status(
                delivery_id=self.delivery.id,
                status=DeliveryStatus.IN_TRANSIT,
            )

    async def test_delete_delivery_success(self):
        # Arrange
        self.mock_delivery_repository.find_by_id.return_value = self.delivery
        self.mock_order_verification_service.verify_order = AsyncMock(return_value=True)

        # Act
        deleted_delivery = await self.delivery_service.delete_delivery(
            delivery_id=self.delivery.id,
        )

        # Assert
        self.mock_delivery_repository.find_by_id.assert_called_once_with(
            self.delivery.id
        )
        self.mock_order_verification_service.verify_order.assert_called_once_with(
            self.delivery.order_id
        )
        self.mock_delivery_repository.delete.assert_called_once_with(self.delivery)
        self.assertEqual(deleted_delivery, self.delivery)

    async def test_delete_delivery_delivery_not_found(self):
        # Arrange
        self.mock_delivery_repository.find_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(EntityNotFound):
            await self.delivery_service.delete_delivery(delivery_id=self.delivery.id)

    def test_list_deliveries(self):
        # Arrange
        self.mock_delivery_repository.list_all.return_value = [self.delivery]

        # Act
        deliveries = self.delivery_service.list_deliveries()

        # Assert
        self.mock_delivery_repository.list_all.assert_called_once()
        self.assertEqual(deliveries, [self.delivery])

    def test_get_customer_by_email(self):
        # Arrange
        self.mock_customer_repository.find_by_email.return_value = self.customer

        # Act
        customer = self.delivery_service.get_customer_by_email(self.customer.email)

        # Assert
        self.mock_customer_repository.find_by_email.assert_called_once_with(
            self.customer.email
        )
        self.assertEqual(customer, self.customer)

    def test_list_customers(self):
        # Arrange
        self.mock_customer_repository.list_all.return_value = [self.customer]

        # Act
        customers = self.delivery_service.list_customers()

        # Assert
        self.mock_customer_repository.list_all.assert_called_once()
        self.assertEqual(customers, [self.customer])

    def test_save_customer(self):
        # Act
        self.delivery_service.save_customer(self.customer)

        # Assert
        self.mock_customer_repository.save.assert_called_once_with(self.customer)

    def test_delete_customer(self):
        # Act
        self.delivery_service.delete_customer(self.customer)

        # Assert
        self.mock_customer_repository.delete.assert_called_once_with(self.customer)


if __name__ == "__main__":
    unittest.main()
