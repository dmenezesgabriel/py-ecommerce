import pytest
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import InvalidEntity


class TestOrderItemEntity:
    def test_order_item_creation_success(self):
        # Arrange
        product_sku = "SKU123"
        quantity = 5
        id = 1

        # Act
        order_item = OrderItemEntity(
            product_sku=product_sku, quantity=quantity, id=id
        )

        # Assert
        assert order_item.id == id
        assert order_item.product_sku == product_sku
        assert order_item.quantity == quantity

    def test_order_item_creation_invalid_id(self):
        # Arrange
        product_sku = "SKU123"
        quantity = 5
        id = -1

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderItemEntity(product_sku=product_sku, quantity=quantity, id=id)
        assert str(exc_info.value) == (
            "Invalid id: -1. ID must be a positive integer or None."
        )

    def test_order_item_creation_invalid_product_sku(self):
        # Arrange
        product_sku = ""
        quantity = 5

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderItemEntity(product_sku=product_sku, quantity=quantity)
        assert str(exc_info.value) == (
            "Invalid product SKU: . SKU must be a non-empty string."
        )

    def test_order_item_creation_invalid_quantity(self):
        # Arrange
        product_sku = "SKU123"
        quantity = -5

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            OrderItemEntity(product_sku=product_sku, quantity=quantity)
        assert str(exc_info.value) == (
            "Invalid quantity: -5. Quantity must be a non-negative integer."
        )

    def test_order_item_setters_success(self):
        # Arrange
        order_item = OrderItemEntity(product_sku="SKU123", quantity=5, id=1)
        new_product_sku = "SKU456"
        new_quantity = 10
        new_id = 2

        # Act
        order_item.product_sku = new_product_sku
        order_item.quantity = new_quantity
        order_item.id = new_id

        # Assert
        assert order_item.product_sku == new_product_sku
        assert order_item.quantity == new_quantity
        assert order_item.id == new_id

    def test_order_item_setters_invalid_id(self):
        # Arrange
        order_item = OrderItemEntity(product_sku="SKU123", quantity=5, id=1)
        invalid_id = -1

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order_item.id = invalid_id
        assert str(exc_info.value) == (
            "Invalid id: -1. ID must be a positive integer or None."
        )

    def test_order_item_setters_invalid_product_sku(self):
        # Arrange
        order_item = OrderItemEntity(product_sku="SKU123", quantity=5, id=1)
        invalid_product_sku = ""

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order_item.product_sku = invalid_product_sku
        assert str(exc_info.value) == (
            "Invalid product SKU: . SKU must be a non-empty string."
        )

    def test_order_item_setters_invalid_quantity(self):
        # Arrange
        order_item = OrderItemEntity(product_sku="SKU123", quantity=5, id=1)
        invalid_quantity = -10

        # Act & Assert
        with pytest.raises(InvalidEntity) as exc_info:
            order_item.quantity = invalid_quantity
        assert str(exc_info.value) == (
            "Invalid quantity: -10. Quantity must be a non-negative integer."
        )

    def test_order_item_to_dict(self):
        # Arrange
        order_item = OrderItemEntity(product_sku="SKU123", quantity=5, id=1)

        # Act
        order_item_dict = order_item.to_dict()

        # Assert
        expected_dict = {
            "id": 1,
            "product_sku": "SKU123",
            "quantity": 5,
        }
        assert order_item_dict == expected_dict


if __name__ == "__main__":
    pytest.main()
