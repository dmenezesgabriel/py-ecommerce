import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from src.adapters.api.customer_api import (
    create_customer,
    delete_customer,
    read_customer,
    read_customers,
    update_customer,
)
from src.application.dto.customer_dto import CustomerCreate
from src.application.services.delivery_service import DeliveryService
from src.domain.entities.customer_entity import CustomerEntity


class TestCustomerAPI(unittest.IsolatedAsyncioTestCase):
    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_read_customers(self, mock_get_delivery_service):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        customer_entity = CustomerEntity(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        mock_service.list_customers.return_value = [customer_entity]

        # Act
        result = await read_customers(mock_service)

        # Assert
        mock_service.list_customers.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, customer_entity.id)
        self.assertEqual(result[0].name, customer_entity.name)
        self.assertEqual(result[0].email, customer_entity.email)

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_read_customer_existing(self, mock_get_delivery_service):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        customer_entity = CustomerEntity(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        mock_service.get_customer_by_email.return_value = customer_entity

        # Act
        result = await read_customer("john@example.com", mock_service)

        # Assert
        mock_service.get_customer_by_email.assert_called_once_with(
            "john@example.com"
        )
        self.assertEqual(result.id, customer_entity.id)
        self.assertEqual(result.name, customer_entity.name)
        self.assertEqual(result.email, customer_entity.email)

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_read_customer_nonexistent(self, mock_get_delivery_service):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        mock_service.get_customer_by_email.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            await read_customer("nonexistent@example.com", mock_service)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Customer not found")

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_create_customer(self, mock_get_delivery_service):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        customer_create = CustomerCreate(
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )

        # The mock should simulate setting the ID after saving the customer
        def save_customer_side_effect(customer_entity):
            customer_entity.id = 1

        mock_service.save_customer.side_effect = save_customer_side_effect

        # Act
        result = await create_customer(customer_create, mock_service)

        # Assert
        mock_service.save_customer.assert_called_once()
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, customer_create.name)
        self.assertEqual(result.email, customer_create.email)

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_update_customer_existing(self, mock_get_delivery_service):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        customer_create = CustomerCreate(
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        customer_entity = CustomerEntity(
            id=1,
            name="Old Name",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        mock_service.get_customer_by_email.return_value = customer_entity

        # Act
        result = await update_customer(
            "john@example.com", customer_create, mock_service
        )

        # Assert
        mock_service.get_customer_by_email.assert_called_once_with(
            "john@example.com"
        )
        mock_service.save_customer.assert_called_once_with(customer_entity)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, customer_create.name)
        self.assertEqual(result.email, customer_create.email)

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_update_customer_nonexistent(
        self, mock_get_delivery_service
    ):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        customer_create = CustomerCreate(
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        mock_service.get_customer_by_email.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            await update_customer(
                "john@example.com", customer_create, mock_service
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Customer not found")

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_delete_customer_existing(self, mock_get_delivery_service):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        customer_entity = CustomerEntity(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        mock_service.get_customer_by_email.return_value = customer_entity

        # Act
        result = await delete_customer("john@example.com", mock_service)

        # Assert
        mock_service.get_customer_by_email.assert_called_once_with(
            "john@example.com"
        )
        mock_service.delete_customer.assert_called_once_with(customer_entity)
        self.assertEqual(result["message"], "Customer deleted successfully")

    @patch("src.adapters.api.customer_api.get_delivery_service")
    async def test_delete_customer_nonexistent(
        self, mock_get_delivery_service
    ):
        # Arrange
        mock_service = MagicMock(spec=DeliveryService)
        mock_get_delivery_service.return_value = mock_service

        mock_service.get_customer_by_email.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            await delete_customer("nonexistent@example.com", mock_service)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Customer not found")


if __name__ == "__main__":
    unittest.main()
