import unittest
from datetime import datetime

from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity, DeliveryStatus
from src.domain.exceptions import InvalidEntity


class TestDeliveryEntity(unittest.TestCase):

    def setUp(self):
        # Common setup for all tests
        self.valid_order_id = 1
        self.valid_delivery_address = "123 Main St"
        self.valid_delivery_date = "2024-08-10"
        self.valid_status = DeliveryStatus.PENDING
        self.valid_customer = CustomerEntity(
            name="John Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
        )
        self.valid_address = AddressEntity(
            city="New York", state="NY", country="USA", zip_code="10001"
        )

    def test_delivery_entity_creation_success(self):
        # Arrange, Act
        delivery = DeliveryEntity(
            order_id=self.valid_order_id,
            delivery_address=self.valid_delivery_address,
            delivery_date=self.valid_delivery_date,
            status=self.valid_status,
            customer=self.valid_customer,
            address=self.valid_address,
        )

        # Assert
        self.assertEqual(delivery.order_id, self.valid_order_id)
        self.assertEqual(
            delivery.delivery_address, self.valid_delivery_address
        )
        self.assertEqual(delivery.delivery_date, self.valid_delivery_date)
        self.assertEqual(delivery.status, self.valid_status)
        self.assertEqual(delivery.customer, self.valid_customer)
        self.assertEqual(delivery.address, self.valid_address)

    def test_delivery_entity_invalid_order_id(self):
        # Arrange
        invalid_order_id = -1

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=invalid_order_id,
                delivery_address=self.valid_delivery_address,
                delivery_date=self.valid_delivery_date,
                status=self.valid_status,
                customer=self.valid_customer,
                address=self.valid_address,
            )
        self.assertEqual(
            str(context.exception), "Order ID must be a positive integer."
        )

    def test_delivery_entity_invalid_delivery_address(self):
        # Arrange
        invalid_delivery_address = "123"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=self.valid_order_id,
                delivery_address=invalid_delivery_address,
                delivery_date=self.valid_delivery_date,
                status=self.valid_status,
                customer=self.valid_customer,
                address=self.valid_address,
            )
        self.assertEqual(
            str(context.exception),
            "Delivery address must be at least 5 characters long.",
        )

    def test_delivery_entity_invalid_delivery_date(self):
        # Arrange
        invalid_delivery_date = "2024-13-01"  # Invalid month

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=self.valid_order_id,
                delivery_address=self.valid_delivery_address,
                delivery_date=invalid_delivery_date,
                status=self.valid_status,
                customer=self.valid_customer,
                address=self.valid_address,
            )
        self.assertEqual(
            str(context.exception),
            "Delivery date must be in the format YYYY-MM-DD.",
        )

    def test_delivery_entity_invalid_status(self):
        # Arrange
        invalid_status = "invalid_status"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=self.valid_order_id,
                delivery_address=self.valid_delivery_address,
                delivery_date=self.valid_delivery_date,
                status=invalid_status,  # Simulating passing invalid status
                customer=self.valid_customer,
                address=self.valid_address,
            )
        self.assertEqual(str(context.exception), "Invalid delivery status.")

    def test_delivery_entity_invalid_customer(self):
        # Arrange
        invalid_customer = "NotACustomerEntity"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=self.valid_order_id,
                delivery_address=self.valid_delivery_address,
                delivery_date=self.valid_delivery_date,
                status=self.valid_status,
                customer=invalid_customer,  # Type mismatch to simulate error
                address=self.valid_address,
            )
        self.assertEqual(
            str(context.exception), "Invalid customer information."
        )

    def test_delivery_entity_invalid_address(self):
        # Arrange
        invalid_address = "NotAnAddressEntity"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=self.valid_order_id,
                delivery_address=self.valid_delivery_address,
                delivery_date=self.valid_delivery_date,
                status=self.valid_status,
                customer=self.valid_customer,
                address=invalid_address,  # Type mismatch to simulate error
            )
        self.assertEqual(
            str(context.exception), "Invalid address information."
        )

    def test_delivery_entity_valid_id(self):
        # Arrange
        valid_id = 10

        # Act
        delivery = DeliveryEntity(
            order_id=self.valid_order_id,
            delivery_address=self.valid_delivery_address,
            delivery_date=self.valid_delivery_date,
            status=self.valid_status,
            customer=self.valid_customer,
            address=self.valid_address,
            id=valid_id,
        )

        # Assert
        self.assertEqual(delivery.id, valid_id)

    def test_delivery_entity_invalid_id(self):
        # Arrange
        invalid_id = -5

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            DeliveryEntity(
                order_id=self.valid_order_id,
                delivery_address=self.valid_delivery_address,
                delivery_date=self.valid_delivery_date,
                status=self.valid_status,
                customer=self.valid_customer,
                address=self.valid_address,
                id=invalid_id,
            )
        self.assertEqual(
            str(context.exception), "ID must be a positive integer."
        )

    def test_update_status_success(self):
        # Arrange
        delivery = DeliveryEntity(
            order_id=self.valid_order_id,
            delivery_address=self.valid_delivery_address,
            delivery_date=self.valid_delivery_date,
            status=self.valid_status,
            customer=self.valid_customer,
            address=self.valid_address,
        )

        # Act
        new_status = DeliveryStatus.IN_TRANSIT
        delivery.update_status(new_status)

        # Assert
        self.assertEqual(delivery.status, new_status)


if __name__ == "__main__":
    unittest.main()
