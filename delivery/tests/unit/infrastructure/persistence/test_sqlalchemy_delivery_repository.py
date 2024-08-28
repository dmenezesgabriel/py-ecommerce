import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session
from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity, DeliveryStatus
from src.infrastructure.persistence.models import (
    AddressModel,
    CustomerModel,
    DeliveryModel,
)
from src.infrastructure.persistence.sqlalchemy_delivery_repository import (
    SQLAlchemyDeliveryRepository,
)


class TestSQLAlchemyDeliveryRepository(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.repository = SQLAlchemyDeliveryRepository(self.mock_db)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.CustomerModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.AddressModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.DeliveryModel"
    )
    def test_save_new_delivery(
        self, mock_delivery_model, mock_address_model, mock_customer_model
    ):
        # Arrange
        customer_entity = CustomerEntity(
            id=None,
            name="John Doe",
            email="john@example.com",
            phone_number="+12345678901234",
        )
        address_entity = AddressEntity(
            id=None,
            city="City",
            state="State",
            country="Country",
            zip_code="12345",
        )
        delivery_entity = DeliveryEntity(
            id=None,
            order_id=1,
            delivery_address="123 Main St",
            delivery_date="2024-08-01",
            status=DeliveryStatus.PENDING,
            customer=customer_entity,
            address=address_entity,
        )

        mock_customer_model.return_value.id = 1
        mock_address_model.return_value.id = 2
        mock_delivery_model.return_value.id = 3

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,
            None,
        ]

        # Act
        self.repository.save(delivery_entity)

        # Assert
        self.mock_db.add.assert_any_call(mock_customer_model.return_value)
        self.mock_db.add.assert_any_call(mock_delivery_model.return_value)
        self.mock_db.add.assert_any_call(mock_address_model.return_value)
        self.mock_db.commit.assert_called()
        self.mock_db.refresh.assert_called()
        self.assertEqual(
            delivery_entity.id, mock_delivery_model.return_value.id
        )
        self.assertEqual(
            delivery_entity.customer.id, mock_customer_model.return_value.id
        )
        self.assertEqual(
            delivery_entity.address.id, mock_address_model.return_value.id
        )

    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.CustomerModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.AddressModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.DeliveryModel"
    )
    def test_find_by_id_existing(
        self, mock_delivery_model, mock_address_model, mock_customer_model
    ):
        # Arrange
        mock_customer_model.id = 1
        mock_customer_model.name = "John Doe"
        mock_customer_model.email = "john@example.com"
        mock_customer_model.phone_number = "+12345678901234"

        mock_address_model.id = 2
        mock_address_model.city = "City"
        mock_address_model.state = "State"
        mock_address_model.country = "Country"
        mock_address_model.zip_code = "12345"

        db_delivery = MagicMock(spec=DeliveryModel)
        db_delivery.id = 1
        db_delivery.order_id = 1
        db_delivery.delivery_address = "123 Main St"
        db_delivery.delivery_date = "2024-08-01"
        db_delivery.status = DeliveryStatus.PENDING
        db_delivery.customer = mock_customer_model
        db_delivery.address = mock_address_model

        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            db_delivery
        )

        # Act
        result = self.repository.find_by_id(1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, db_delivery.id)
        self.assertEqual(result.customer.id, mock_customer_model.id)
        self.assertEqual(result.address.id, mock_address_model.id)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.CustomerModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.AddressModel"
    )
    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.DeliveryModel"
    )
    def test_find_by_order_id_existing(
        self, mock_delivery_model, mock_address_model, mock_customer_model
    ):
        # Arrange
        mock_customer_model.id = 1
        mock_customer_model.name = "John Doe"
        mock_customer_model.email = "john@example.com"
        mock_customer_model.phone_number = "+12345678901234"

        mock_address_model.id = 2
        mock_address_model.city = "City"
        mock_address_model.state = "State"
        mock_address_model.country = "Country"
        mock_address_model.zip_code = "12345"

        db_delivery = MagicMock(spec=DeliveryModel)
        db_delivery.id = 1
        db_delivery.order_id = 1
        db_delivery.delivery_address = "123 Main St"
        db_delivery.delivery_date = "2024-08-01"
        db_delivery.status = DeliveryStatus.PENDING
        db_delivery.customer = mock_customer_model
        db_delivery.address = mock_address_model

        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            db_delivery
        )

        # Act
        result = self.repository.find_by_order_id(1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.order_id, db_delivery.order_id)
        self.assertEqual(result.customer.id, mock_customer_model.id)
        self.assertEqual(result.address.id, mock_address_model.id)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.DeliveryModel"
    )
    def test_list_all(self, mock_delivery_model):
        # Arrange
        mock_customer_model_1 = MagicMock(spec=CustomerModel)
        mock_customer_model_1.id = 1
        mock_customer_model_1.name = "John Doe"
        mock_customer_model_1.email = "john@example.com"
        mock_customer_model_1.phone_number = "+12345678901234"

        mock_address_model_1 = MagicMock(spec=AddressModel)
        mock_address_model_1.id = 2
        mock_address_model_1.city = "City"
        mock_address_model_1.state = "State"
        mock_address_model_1.country = "Country"
        mock_address_model_1.zip_code = "12345"

        db_delivery1 = MagicMock(spec=DeliveryModel)
        db_delivery1.id = 1
        db_delivery1.order_id = 1
        db_delivery1.delivery_address = "123 Main St"
        db_delivery1.delivery_date = "2024-08-01"
        db_delivery1.status = DeliveryStatus.PENDING
        db_delivery1.customer = mock_customer_model_1
        db_delivery1.address = mock_address_model_1

        mock_customer_model_2 = MagicMock(spec=CustomerModel)
        mock_customer_model_2.id = 2
        mock_customer_model_2.name = "Jane Smith"
        mock_customer_model_2.email = "jane@example.com"
        mock_customer_model_2.phone_number = "+12345678909876"

        mock_address_model_2 = MagicMock(spec=AddressModel)
        mock_address_model_2.id = 3
        mock_address_model_2.city = "Another City"
        mock_address_model_2.state = "Another State"
        mock_address_model_2.country = "Another Country"
        mock_address_model_2.zip_code = "67890"

        db_delivery2 = MagicMock(spec=DeliveryModel)
        db_delivery2.id = 2
        db_delivery2.order_id = 2
        db_delivery2.delivery_address = "456 Elm St"
        db_delivery2.delivery_date = "2024-08-02"
        db_delivery2.status = DeliveryStatus.DELIVERED
        db_delivery2.customer = mock_customer_model_2
        db_delivery2.address = mock_address_model_2

        self.mock_db.query.return_value.all.return_value = [
            db_delivery1,
            db_delivery2,
        ]

        # Act
        result = self.repository.list_all()

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, db_delivery1.id)
        self.assertEqual(result[1].id, db_delivery2.id)

    @patch(
        "src.infrastructure.persistence.sqlalchemy_delivery_repository.DeliveryModel"
    )
    def test_delete_existing_delivery(self, mock_delivery_model):
        # Arrange
        delivery_entity = DeliveryEntity(
            id=1,
            order_id=1,
            delivery_address="123 Main St",
            delivery_date="2024-08-01",
            status=DeliveryStatus.PENDING,
            customer=CustomerEntity(
                id=1,
                name="John Doe",
                email="john@example.com",
                phone_number="+12345678901234",
            ),
            address=AddressEntity(
                id=2,
                city="City",
                state="State",
                country="Country",
                zip_code="12345",
            ),
        )

        db_delivery = MagicMock(spec=DeliveryModel)
        db_delivery.id = delivery_entity.id
        db_delivery.address = MagicMock(spec=AddressModel)

        self.mock_db.query.return_value.filter.return_value.first.return_value = (
            db_delivery
        )

        # Act
        self.repository.delete(delivery_entity)

        # Assert
        self.mock_db.delete.assert_any_call(db_delivery.address)
        self.mock_db.delete.assert_any_call(db_delivery)
        self.mock_db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
