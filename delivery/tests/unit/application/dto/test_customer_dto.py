import unittest

from src.application.dto.customer_dto import CustomerCreate, CustomerResponse


class TestCustomerDTO(unittest.TestCase):

    def test_customer_create_dto(self):
        # Arrange
        data = {
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "phone_number": "+11234567890",
        }

        # Act
        customer = CustomerCreate(**data)

        # Assert
        self.assertEqual(customer.name, data["name"])
        self.assertEqual(customer.email, data["email"])
        self.assertEqual(customer.phone_number, data["phone_number"])

    def test_customer_create_dto_without_phone_number(self):
        # Arrange
        data = {
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
        }

        # Act
        customer = CustomerCreate(**data)

        # Assert
        self.assertEqual(customer.name, data["name"])
        self.assertEqual(customer.email, data["email"])
        self.assertIsNone(customer.phone_number)

    def test_customer_response_dto(self):
        # Arrange
        data = {
            "id": 1,
            "name": "Alice Smith",
            "email": "alice.smith@example.com",
            "phone_number": "+11234567890",
        }

        # Act
        customer_response = CustomerResponse(**data)

        # Assert
        self.assertEqual(customer_response.id, data["id"])
        self.assertEqual(customer_response.name, data["name"])
        self.assertEqual(customer_response.email, data["email"])
        self.assertEqual(customer_response.phone_number, data["phone_number"])

    def test_customer_response_dto_without_phone_number(self):
        # Arrange
        data = {
            "id": 2,
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
        }

        # Act
        customer_response = CustomerResponse(**data)

        # Assert
        self.assertEqual(customer_response.id, data["id"])
        self.assertEqual(customer_response.name, data["name"])
        self.assertEqual(customer_response.email, data["email"])
        self.assertIsNone(customer_response.phone_number)

    def test_customer_create_examples(self):
        # Arrange
        examples = CustomerCreate.model_config["json_schema_extra"]["examples"]

        # Act
        example_1 = CustomerCreate(**examples[0])
        example_2 = CustomerCreate(**examples[1])

        # Assert
        self.assertEqual(example_1.name, "Alice Smith")
        self.assertEqual(example_1.email, "alice.smith@example.com")
        self.assertEqual(example_1.phone_number, "+11234567890")

        self.assertEqual(example_2.name, "Bob Johnson")
        self.assertEqual(example_2.email, "bob.johnson@example.com")
        self.assertIsNone(example_2.phone_number)

    def test_customer_response_examples(self):
        # Arrange
        examples = CustomerResponse.model_config["json_schema_extra"][
            "examples"
        ]

        # Act
        example_1 = CustomerResponse(**examples[0])
        example_2 = CustomerResponse(**examples[1])

        # Assert
        self.assertEqual(example_1.id, 1)
        self.assertEqual(example_1.name, "Alice Smith")
        self.assertEqual(example_1.email, "alice.smith@example.com")
        self.assertEqual(example_1.phone_number, "+11234567890")

        self.assertEqual(example_2.id, 2)
        self.assertEqual(example_2.name, "Bob Johnson")
        self.assertEqual(example_2.email, "bob.johnson@example.com")
        self.assertIsNone(example_2.phone_number)


if __name__ == "__main__":
    unittest.main()
