import unittest

from src.application.dto.delivery_dto import (
    AddressCreate,
    AddressResponse,
    DeliveryCreate,
    DeliveryResponse,
    DeliveryStatusUpdate,
)
from src.domain.entities.delivery_entity import DeliveryStatus


class TestDeliveryDTO(unittest.TestCase):

    def test_address_create_dto(self):
        # Arrange
        data = {
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "zip_code": "10001",
        }

        # Act
        address = AddressCreate(**data)

        # Assert
        self.assertEqual(address.city, data["city"])
        self.assertEqual(address.state, data["state"])
        self.assertEqual(address.country, data["country"])
        self.assertEqual(address.zip_code, data["zip_code"])

    def test_delivery_create_dto(self):
        # Arrange
        data = {
            "order_id": 123,
            "delivery_address": "123 Main St, Apt 4B",
            "delivery_date": "2024-08-20",
            "status": DeliveryStatus.PENDING,
            "address": {
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "zip_code": "10001",
            },
            "customer": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone_number": "+123456789",
            },
        }

        # Act
        delivery = DeliveryCreate(**data)

        # Assert
        self.assertEqual(delivery.order_id, data["order_id"])
        self.assertEqual(delivery.delivery_address, data["delivery_address"])
        self.assertEqual(delivery.delivery_date, data["delivery_date"])
        self.assertEqual(delivery.status, data["status"])
        self.assertEqual(delivery.address.city, data["address"]["city"])
        self.assertEqual(delivery.customer.name, data["customer"]["name"])

    def test_delivery_status_update_dto(self):
        # Arrange
        data = {"status": DeliveryStatus.IN_TRANSIT}

        # Act
        status_update = DeliveryStatusUpdate(**data)

        # Assert
        self.assertEqual(status_update.status, data["status"])

    def test_address_response_dto(self):
        # Arrange
        data = {
            "id": 1,
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "zip_code": "10001",
        }

        # Act
        address_response = AddressResponse(**data)

        # Assert
        self.assertEqual(address_response.id, data["id"])
        self.assertEqual(address_response.city, data["city"])
        self.assertEqual(address_response.state, data["state"])
        self.assertEqual(address_response.country, data["country"])
        self.assertEqual(address_response.zip_code, data["zip_code"])

    def test_delivery_response_dto(self):
        # Arrange
        data = {
            "id": 1,
            "order_id": 123,
            "delivery_address": "123 Main St, Apt 4B",
            "delivery_date": "2024-08-20",
            "status": DeliveryStatus.PENDING,
            "address": {
                "id": 1,
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "zip_code": "10001",
            },
            "customer": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone_number": "+123456789",
            },
        }

        # Act
        delivery_response = DeliveryResponse(**data)

        # Assert
        self.assertEqual(delivery_response.id, data["id"])
        self.assertEqual(delivery_response.order_id, data["order_id"])
        self.assertEqual(
            delivery_response.delivery_address, data["delivery_address"]
        )
        self.assertEqual(
            delivery_response.delivery_date, data["delivery_date"]
        )
        self.assertEqual(delivery_response.status, data["status"])
        self.assertEqual(
            delivery_response.address.city, data["address"]["city"]
        )
        self.assertEqual(
            delivery_response.customer.name, data["customer"]["name"]
        )

    def test_address_create_examples(self):
        # Arrange
        examples = AddressCreate.model_config["json_schema_extra"]["examples"]

        # Act
        example_1 = AddressCreate(**examples[0])
        example_2 = AddressCreate(**examples[1])

        # Assert
        self.assertEqual(example_1.city, "New York")
        self.assertEqual(example_1.state, "NY")
        self.assertEqual(example_1.country, "USA")
        self.assertEqual(example_1.zip_code, "10001")

        self.assertEqual(example_2.city, "Los Angeles")
        self.assertEqual(example_2.state, "CA")
        self.assertEqual(example_2.country, "USA")
        self.assertEqual(example_2.zip_code, "90001")

    def test_delivery_create_examples(self):
        # Arrange
        examples = DeliveryCreate.model_config["json_schema_extra"]["examples"]

        # Act
        example_1 = DeliveryCreate(**examples[0])

        # Assert
        self.assertEqual(example_1.order_id, 123)
        self.assertEqual(example_1.delivery_address, "123 Main St, Apt 4B")
        self.assertEqual(example_1.delivery_date, "2024-08-20")
        self.assertEqual(example_1.status, DeliveryStatus.PENDING)
        self.assertEqual(example_1.address.city, "New York")
        self.assertEqual(example_1.customer.name, "John Doe")

    def test_delivery_status_update_examples(self):
        # Arrange
        examples = DeliveryStatusUpdate.model_config["json_schema_extra"][
            "examples"
        ]

        # Act
        example_1 = DeliveryStatusUpdate(**examples[0])
        example_2 = DeliveryStatusUpdate(**examples[1])

        # Assert
        self.assertEqual(example_1.status, DeliveryStatus.IN_TRANSIT)
        self.assertEqual(example_2.status, DeliveryStatus.DELIVERED)

    def test_address_response_examples(self):
        # Arrange
        examples = AddressResponse.model_config["json_schema_extra"][
            "examples"
        ]

        # Act
        example_1 = AddressResponse(**examples[0])
        example_2 = AddressResponse(**examples[1])

        # Assert
        self.assertEqual(example_1.id, 1)
        self.assertEqual(example_1.city, "New York")
        self.assertEqual(example_1.state, "NY")
        self.assertEqual(example_1.country, "USA")
        self.assertEqual(example_1.zip_code, "10001")

        self.assertEqual(example_2.id, 2)
        self.assertEqual(example_2.city, "Los Angeles")
        self.assertEqual(example_2.state, "CA")
        self.assertEqual(example_2.country, "USA")
        self.assertEqual(example_2.zip_code, "90001")

    def test_delivery_response_examples(self):
        # Arrange
        examples = DeliveryResponse.model_config["json_schema_extra"][
            "examples"
        ]

        # Act
        example_1 = DeliveryResponse(**examples[0])

        # Assert
        self.assertEqual(example_1.id, 1)
        self.assertEqual(example_1.order_id, 123)
        self.assertEqual(example_1.delivery_address, "123 Main St, Apt 4B")
        self.assertEqual(example_1.delivery_date, "2024-08-20")
        self.assertEqual(example_1.status, DeliveryStatus.PENDING)
        self.assertEqual(example_1.address.city, "New York")
        self.assertEqual(example_1.customer.name, "John Doe")


if __name__ == "__main__":
    unittest.main()
