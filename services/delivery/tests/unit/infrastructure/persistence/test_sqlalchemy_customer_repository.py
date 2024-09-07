import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from src.domain.entities.customer_entity import CustomerEntity
from src.infrastructure.persistence.models import CustomerModel
from src.infrastructure.persistence.sqlalchemy_customer_repository import (
    SQLAlchemyCustomerRepository,
)


class TestSQLAlchemyCustomerRepository(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.repository = SQLAlchemyCustomerRepository(self.mock_db)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_customer_repository.CustomerModel"
    )
    def test_save_new_customer(self, mock_customer_model):
        # Arrange
        customer_entity = CustomerEntity(
            id=None,
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        mock_db_customer = MagicMock(spec=CustomerModel)
        mock_db_customer.id = 1  # Set a valid integer ID
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )
        mock_customer_model.return_value = mock_db_customer

        # Act
        self.repository.save(customer_entity)

        # Assert
        self.mock_db.add.assert_called_once_with(
            mock_customer_model.return_value
        )
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(
            mock_customer_model.return_value
        )
        self.assertEqual(
            customer_entity.id, mock_customer_model.return_value.id
        )

    @patch(
        "src.infrastructure.persistence.sqlalchemy_customer_repository.CustomerModel"
    )
    def test_save_existing_customer(self, mock_customer_model):
        # Arrange
        customer_entity = CustomerEntity(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        db_customer = MagicMock(spec=CustomerModel)
        db_customer.id = 1  # Set a valid integer ID
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            db_customer
        )

        # Act
        self.repository.save(customer_entity)

        # Assert
        self.mock_db.add.assert_not_called()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(db_customer)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_customer_repository.CustomerModel"
    )
    def test_find_by_email_existing(self, mock_customer_model):
        # Arrange
        db_customer = MagicMock(spec=CustomerModel)
        db_customer.id = 1
        db_customer.name = "John Doe"
        db_customer.email = "john@example.com"
        db_customer.phone_number = "+12345678901234"
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            db_customer
        )

        # Act
        result = self.repository.find_by_email("john@example.com")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, db_customer.id)
        self.assertEqual(result.name, db_customer.name)
        self.assertEqual(result.email, db_customer.email)
        self.assertEqual(result.phone_number, db_customer.phone_number)

    def test_find_by_email_nonexistent(self):
        # Arrange
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        # Act
        result = self.repository.find_by_email("nonexistent@example.com")

        # Assert
        self.assertIsNone(result)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_customer_repository.CustomerModel"
    )
    def test_list_all(self, mock_customer_model):
        # Arrange
        db_customer1 = MagicMock(spec=CustomerModel)
        db_customer1.id = 1
        db_customer1.name = "John Doe"
        db_customer1.email = "john@example.com"
        db_customer1.phone_number = "+12345678901234"
        db_customer2 = MagicMock(spec=CustomerModel)
        db_customer2.id = 2
        db_customer2.name = "Jane Smith"
        db_customer2.email = "jane@example.com"
        db_customer2.phone_number = "+12345678901234"
        self.mock_db.query.return_value.filter.return_value.all.return_value = [
            db_customer1,
            db_customer2,
        ]

        # Act
        result = self.repository.list_all()

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, db_customer1.id)
        self.assertEqual(result[0].name, db_customer1.name)
        self.assertEqual(result[0].email, db_customer1.email)
        self.assertEqual(result[0].phone_number, db_customer1.phone_number)
        self.assertEqual(result[1].id, db_customer2.id)
        self.assertEqual(result[1].name, db_customer2.name)
        self.assertEqual(result[1].email, db_customer2.email)
        self.assertEqual(result[1].phone_number, db_customer2.phone_number)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_customer_repository.CustomerModel"
    )
    def test_delete_existing_customer(self, mock_customer_model):
        # Arrange
        customer_entity = CustomerEntity(
            id=1, name="John Doe", email="john@example.com"
        )
        db_customer = MagicMock(spec=CustomerModel)
        db_customer.id = customer_entity.id
        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            db_customer
        )

        # Act
        self.repository.delete(customer_entity)

        # Assert
        self.assertEqual(db_customer.name, f"deleted_user_{db_customer.id}")
        self.assertEqual(
            db_customer.email, f"deleted_email_{db_customer.id}@example.com"
        )
        self.assertEqual(
            db_customer.phone_number, f"deleted_phone_number_{db_customer.id}"
        )
        self.assertEqual(db_customer.deleted, 1)
        self.mock_db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
