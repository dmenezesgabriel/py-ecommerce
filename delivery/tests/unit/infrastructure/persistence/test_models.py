import unittest
from unittest.mock import patch

from sqlalchemy import Enum, Integer, String
from src.infrastructure.persistence.models import (
    AddressModel,
    CustomerModel,
    DeliveryModel,
)


class TestDeliveryModel(unittest.TestCase):
    @patch("src.infrastructure.persistence.models.Base.metadata")
    def test_delivery_model_columns(self, mock_metadata):
        # Assert
        self.assertTrue(hasattr(DeliveryModel, "id"))
        self.assertIsInstance(
            DeliveryModel.id.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(DeliveryModel, "order_id"))
        self.assertIsInstance(
            DeliveryModel.order_id.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(DeliveryModel, "delivery_address"))
        self.assertIsInstance(
            DeliveryModel.delivery_address.property.columns[0].type, String
        )
        self.assertTrue(hasattr(DeliveryModel, "delivery_date"))
        self.assertIsInstance(
            DeliveryModel.delivery_date.property.columns[0].type, String
        )
        self.assertTrue(hasattr(DeliveryModel, "status"))
        self.assertIsInstance(
            DeliveryModel.status.property.columns[0].type, Enum
        )
        self.assertTrue(hasattr(DeliveryModel, "customer_id"))
        self.assertIsInstance(
            DeliveryModel.customer_id.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(DeliveryModel, "address_id"))
        self.assertIsInstance(
            DeliveryModel.address_id.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(DeliveryModel, "customer"))
        self.assertTrue(hasattr(DeliveryModel, "address"))


class TestCustomerModel(unittest.TestCase):
    @patch("src.infrastructure.persistence.models.Base.metadata")
    def test_customer_model_columns(self, mock_metadata):
        # Assert
        self.assertTrue(hasattr(CustomerModel, "id"))
        self.assertIsInstance(
            CustomerModel.id.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(CustomerModel, "name"))
        self.assertIsInstance(
            CustomerModel.name.property.columns[0].type, String
        )
        self.assertTrue(hasattr(CustomerModel, "email"))
        self.assertIsInstance(
            CustomerModel.email.property.columns[0].type, String
        )
        self.assertTrue(hasattr(CustomerModel, "phone_number"))
        self.assertIsInstance(
            CustomerModel.phone_number.property.columns[0].type, String
        )
        self.assertTrue(hasattr(CustomerModel, "deleted"))
        self.assertIsInstance(
            CustomerModel.deleted.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(CustomerModel, "deliveries"))


class TestAddressModel(unittest.TestCase):
    @patch("src.infrastructure.persistence.models.Base.metadata")
    def test_address_model_columns(self, mock_metadata):

        # Assert
        self.assertTrue(hasattr(AddressModel, "id"))
        self.assertIsInstance(
            AddressModel.id.property.columns[0].type, Integer
        )
        self.assertTrue(hasattr(AddressModel, "city"))
        self.assertIsInstance(
            AddressModel.city.property.columns[0].type, String
        )
        self.assertTrue(hasattr(AddressModel, "state"))
        self.assertIsInstance(
            AddressModel.state.property.columns[0].type, String
        )
        self.assertTrue(hasattr(AddressModel, "country"))
        self.assertIsInstance(
            AddressModel.country.property.columns[0].type, String
        )
        self.assertTrue(hasattr(AddressModel, "zip_code"))
        self.assertIsInstance(
            AddressModel.zip_code.property.columns[0].type, String
        )
        self.assertTrue(hasattr(AddressModel, "delivery"))


if __name__ == "__main__":
    unittest.main()
