import unittest

from src.domain.entities.customer_entity import CustomerEntity
from src.domain.exceptions import InvalidEntity


class TestCustomerEntity(unittest.TestCase):

    def test_customer_creation_success(self):
        # Arrange
        name = "John Doe"
        email = "john.doe@example.com"
        phone_number = "+123456789"
        id = 1

        # Act
        customer = CustomerEntity(
            name=name, email=email, phone_number=phone_number, id=id
        )

        # Assert
        self.assertEqual(customer.id, id)
        self.assertEqual(customer.name, name)
        self.assertEqual(customer.email, email)
        self.assertEqual(customer.phone_number, phone_number)

    def test_customer_creation_invalid_name(self):
        # Arrange
        name = "J"
        email = "john.doe@example.com"
        phone_number = "+123456789"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            CustomerEntity(name=name, email=email, phone_number=phone_number)
        self.assertEqual(
            str(context.exception), "Name must be at least 2 characters long."
        )

    def test_customer_creation_invalid_email(self):
        # Arrange
        name = "John Doe"
        email = "john.doe"
        phone_number = "+123456789"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            CustomerEntity(name=name, email=email, phone_number=phone_number)
        self.assertEqual(str(context.exception), "Invalid email format.")

    def test_customer_creation_invalid_phone_number(self):
        # Arrange
        name = "John Doe"
        email = "john.doe@example.com"
        phone_number = "123456"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            CustomerEntity(name=name, email=email, phone_number=phone_number)
        self.assertEqual(
            str(context.exception), "Invalid phone number format."
        )

    def test_customer_creation_invalid_id(self):
        # Arrange
        name = "John Doe"
        email = "john.doe@example.com"
        phone_number = "+123456789"
        id = -1

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            CustomerEntity(
                name=name, email=email, phone_number=phone_number, id=id
            )
        self.assertEqual(
            str(context.exception), "ID must be a positive integer."
        )

    def test_update_customer_name(self):
        # Arrange
        customer = CustomerEntity(
            name="John Doe", email="john.doe@example.com"
        )
        new_name = "Jane Doe"

        # Act
        customer.update_customer(name=new_name)

        # Assert
        self.assertEqual(customer.name, new_name)

    def test_update_customer_email(self):
        # Arrange
        customer = CustomerEntity(
            name="John Doe", email="john.doe@example.com"
        )
        new_email = "jane.doe@example.com"

        # Act
        customer.update_customer(email=new_email)

        # Assert
        self.assertEqual(customer.email, new_email)

    def test_update_customer_phone_number(self):
        # Arrange
        customer = CustomerEntity(
            name="John Doe", email="john.doe@example.com"
        )
        new_phone_number = "+987654321"

        # Act
        customer.update_customer(phone_number=new_phone_number)

        # Assert
        self.assertEqual(customer.phone_number, new_phone_number)

    def test_to_dict(self):
        # Arrange
        customer = CustomerEntity(
            name="John Doe", email="john.doe@example.com", id=1
        )

        # Act
        customer_dict = customer.to_dict()

        # Assert
        expected_dict = {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": None,
        }
        self.assertEqual(customer_dict, expected_dict)


if __name__ == "__main__":
    unittest.main()
