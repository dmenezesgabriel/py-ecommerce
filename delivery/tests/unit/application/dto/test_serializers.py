import unittest

from src.application.dto.serializers import (
    serialize_customer,
    serialize_delivery,
)
from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity, DeliveryStatus


class TestSerializers(unittest.TestCase):

    def setUp(self):
        # Arrange common data
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

    def test_serialize_delivery(self):
        # Act
        delivery_response = serialize_delivery(self.delivery)

        # Assert
        self.assertEqual(delivery_response.id, self.delivery.id)
        self.assertEqual(delivery_response.order_id, self.delivery.order_id)
        self.assertEqual(
            delivery_response.delivery_address, self.delivery.delivery_address
        )
        self.assertEqual(
            delivery_response.delivery_date, self.delivery.delivery_date
        )
        self.assertEqual(delivery_response.status, self.delivery.status)
        self.assertEqual(delivery_response.customer.id, self.customer.id)
        self.assertEqual(delivery_response.customer.name, self.customer.name)
        self.assertEqual(delivery_response.customer.email, self.customer.email)
        self.assertEqual(
            delivery_response.customer.phone_number,
            self.customer.phone_number,
        )
        self.assertEqual(delivery_response.address.id, self.address.id)
        self.assertEqual(delivery_response.address.city, self.address.city)
        self.assertEqual(delivery_response.address.state, self.address.state)
        self.assertEqual(
            delivery_response.address.country, self.address.country
        )
        self.assertEqual(
            delivery_response.address.zip_code, self.address.zip_code
        )

    def test_serialize_customer(self):
        # Act
        customer_response = serialize_customer(self.customer)

        # Assert
        self.assertEqual(customer_response.id, self.customer.id)
        self.assertEqual(customer_response.name, self.customer.name)
        self.assertEqual(customer_response.email, self.customer.email)
        self.assertEqual(
            customer_response.phone_number, self.customer.phone_number
        )


if __name__ == "__main__":
    unittest.main()
