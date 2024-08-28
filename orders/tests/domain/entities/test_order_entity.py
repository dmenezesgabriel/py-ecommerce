from unittest.mock import Mock

import pytest
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import InvalidEntity


class TestOrderEntity:
    def test_order_entity_creation_success(self):
        # Arrange
        customer = Mock(spec=CustomerEntity)
        order_items = [Mock(spec=OrderItemEntity)]
        status = OrderStatus.CONFIRMED
        id = 1
        order_number = "ORD123"
        total_amount = 100.0

        # Act
        order = OrderEntity(
            customer=customer,
            order_items=order_items,
            status=status,
            id=id,
            order_number=order_number,
            total_amount=total_amount,
        )

        # Assert
        assert order.id == id
        assert order.order_number == order_number
        assert order.customer == customer
        assert order.order_items == order_items
        assert order.status == status
        assert order.total_amount == total_amount

    def test_order_entity_creation_invalid_id(self):
        # Arrange
        customer = Mock(spec=CustomerEntity)
        order_items = [Mock(spec=OrderItemEntity)]
        invalid_id = -1

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderEntity(
                customer=customer, order_items=order_items, id=invalid_id
            )
        assert str(exc_info.value) == (
            "Invalid id: -1. ID must be a positive integer or None."
        )

    def test_order_entity_creation_invalid_order_number(self):
        # Arrange
        customer = Mock(spec=CustomerEntity)
        order_items = [Mock(spec=OrderItemEntity)]
        invalid_order_number = 1

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderEntity(
                customer=customer,
                order_items=order_items,
                order_number=invalid_order_number,
            )
        assert str(exc_info.value) == (
            "Invalid order number: 1. Order number must be a non-empty string."
        )

    def test_order_entity_creation_invalid_customer(self):
        # Arrange
        invalid_customer = "not a customer entity"
        order_items = [Mock(spec=OrderItemEntity)]

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderEntity(customer=invalid_customer, order_items=order_items)
        assert str(exc_info.value) == (
            "Invalid customer. Must be a CustomerEntity instance."
        )

    def test_order_entity_creation_invalid_order_items(self):
        # Arrange
        customer = Mock(spec=CustomerEntity)
        invalid_order_items = ["not an order item entity"]

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderEntity(customer=customer, order_items=invalid_order_items)
        assert str(exc_info.value) == (
            "Invalid order items. Must be a list of OrderItemEntity instances."
        )

    def test_order_entity_creation_invalid_total_amount(self):
        # Arrange
        customer = Mock(spec=CustomerEntity)
        order_items = [Mock(spec=OrderItemEntity)]
        invalid_total_amount = -100.0

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderEntity(
                customer=customer,
                order_items=order_items,
                total_amount=invalid_total_amount,
            )
        assert str(exc_info.value) == (
            "Invalid total amount: -100.0. Total amount must be a non-negative number."
        )

    def test_order_entity_setters_success(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        new_customer = Mock(spec=CustomerEntity)
        new_order_items = [Mock(spec=OrderItemEntity)]
        new_order_number = "NEW123"
        new_total_amount = 200.0
        new_id = 2
        new_status = OrderStatus.SHIPPED

        # Act
        order.customer = new_customer
        order.order_items = new_order_items
        order.order_number = new_order_number
        order.total_amount = new_total_amount
        order.id = new_id
        order.status = new_status

        # Assert
        assert order.customer == new_customer
        assert order.order_items == new_order_items
        assert order.order_number == new_order_number
        assert order.total_amount == new_total_amount
        assert order.id == new_id
        assert order.status == new_status

    def test_order_entity_setters_invalid_id(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        invalid_id = -2

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order.id = invalid_id
        assert str(exc_info.value) == (
            "Invalid id: -2. ID must be a positive integer or None."
        )

    def test_order_entity_setters_invalid_order_number(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        invalid_order_number = ""

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order.order_number = invalid_order_number
        assert str(exc_info.value) == (
            "Invalid order number: . Order number must be a non-empty string."
        )

    def test_order_entity_setters_invalid_customer(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        invalid_customer = "not a customer entity"

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order.customer = invalid_customer
        assert str(exc_info.value) == (
            "Invalid customer. Must be a CustomerEntity instance."
        )

    def test_order_entity_setters_invalid_order_items(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        invalid_order_items = ["not an order item entity"]

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order.order_items = invalid_order_items
        assert str(exc_info.value) == (
            "Invalid order items. Must be a list of OrderItemEntity instances."
        )

    def test_order_entity_setters_invalid_total_amount(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        invalid_total_amount = -100.0

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order.total_amount = invalid_total_amount
        assert str(exc_info.value) == (
            "Invalid total amount: -100.0. Total amount must be a non-negative number."
        )

    def test_order_entity_add_item(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        new_order_item = Mock(spec=OrderItemEntity)

        # Act
        order.add_item(new_order_item)

        # Assert
        assert new_order_item in order.order_items

    def test_order_entity_update_status(self):
        # Arrange
        order = OrderEntity(
            customer=Mock(spec=CustomerEntity),
            order_items=[Mock(spec=OrderItemEntity)],
        )
        new_status = OrderStatus.PAID

        # Act
        order.update_status(new_status)

        # Assert
        assert order.status == new_status

    def test_order_entity_to_dict(self):
        # Arrange
        customer = Mock(spec=CustomerEntity)
        customer.to_dict.return_value = {"id": 1, "name": "John Doe"}
        order_items = [Mock(spec=OrderItemEntity)]
        order_items[0].to_dict.return_value = {
            "id": 1,
            "product_sku": "SKU123",
            "quantity": 2,
        }
        order = OrderEntity(
            customer=customer,
            order_items=order_items,
            id=1,
            order_number="ORD123",
            status=OrderStatus.CONFIRMED,
            total_amount=100.0,
        )

        # Act
        order_dict = order.to_dict()

        # Assert
        expected_dict = {
            "id": 1,
            "order_number": "ORD123",
            "customer": {"id": 1, "name": "John Doe"},
            "order_items": [{"id": 1, "product_sku": "SKU123", "quantity": 2}],
            "status": "confirmed",
            "total_amount": 100.0,
        }
        assert order_dict == expected_dict


if __name__ == "__main__":
    pytest.main()
