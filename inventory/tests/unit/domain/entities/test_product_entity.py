from unittest.mock import Mock

import pytest
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.inventory_entity import InventoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.entities.product_entity import ProductEntity
from src.domain.exceptions import InvalidEntity


class TestProductEntity:

    def test_create_valid_product(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)

        # Act
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
            description="Product Description",
            images=["http://example.com"],
        )

        # Assert
        assert product.id == 1
        assert product.sku == "ABC123"
        assert product.name == "Product Name"
        assert product.category == category
        assert product.price == price
        assert product.inventory == inventory
        assert product.description == "Product Description"
        assert product.images == ["http://example.com"]

    def test_create_product_invalid_id(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            ProductEntity(
                sku="ABC123",
                name="Product Name",
                category=category,
                price=price,
                inventory=inventory,
                id=-1,
            )

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_create_product_invalid_sku(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            ProductEntity(
                sku="",
                name="Product Name",
                category=category,
                price=price,
                inventory=inventory,
                id=1,
            )

        # Assert
        assert "Invalid SKU" in str(exc_info.value)

    def test_create_product_invalid_name(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            ProductEntity(
                sku="ABC123",
                name="",
                category=category,
                price=price,
                inventory=inventory,
                id=1,
            )

        # Assert
        assert "Invalid name" in str(exc_info.value)

    def test_set_valid_id(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.id = 2

        # Assert
        assert product.id == 2

    def test_set_invalid_id(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.id = -2

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_set_valid_sku(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.sku = "XYZ789"

        # Assert
        assert product.sku == "XYZ789"

    def test_set_invalid_sku(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.sku = ""

        # Assert
        assert "Invalid SKU" in str(exc_info.value)

    def test_set_valid_name(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.name = "New Product Name"

        # Assert
        assert product.name == "New Product Name"

    def test_set_invalid_name(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.name = ""

        # Assert
        assert "Invalid name" in str(exc_info.value)

    def test_set_invalid_category(self):
        # Arrange
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=Mock(spec=CategoryEntity),
            price=Mock(spec=PriceEntity),
            inventory=Mock(spec=InventoryEntity),
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.category = "Invalid Category"

        # Assert
        assert "Invalid category" in str(exc_info.value)

    def test_set_invalid_price(self):
        # Arrange
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=Mock(spec=CategoryEntity),
            price=Mock(spec=PriceEntity),
            inventory=Mock(spec=InventoryEntity),
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.price = "Invalid Price"

        # Assert
        assert "Invalid price" in str(exc_info.value)

    def test_set_invalid_inventory(self):
        # Arrange
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=Mock(spec=CategoryEntity),
            price=Mock(spec=PriceEntity),
            inventory=Mock(spec=InventoryEntity),
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.inventory = "Invalid Inventory"

        # Assert
        assert "Invalid inventory" in str(exc_info.value)

    def test_set_inventory(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.set_inventory(50)

        # Assert
        inventory.set_quantity.assert_called_once_with(50)

    def test_set_price(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.set_price(199.99)

        # Assert
        assert price.amount == 199.99

    def test_add_inventory(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity, quantity=100)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.add_inventory(50)

        # Assert
        assert product.inventory.quantity == 150

    def test_add_inventory_invalid_quantity(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.add_inventory(-10)

        # Assert
        assert "Quantity to add must be positive" in str(exc_info.value)

    def test_subtract_inventory(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity, quantity=100)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act
        product.subtract_inventory(50)

        # Assert
        assert product.inventory.quantity == 50

    def test_subtract_inventory_invalid_quantity(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.subtract_inventory(-10)

        # Assert
        assert "Quantity to subtract must be positive" in str(exc_info.value)

    def test_subtract_inventory_exceeds_quantity(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        price = Mock(spec=PriceEntity)
        inventory = Mock(spec=InventoryEntity, quantity=50)
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
        )

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            product.subtract_inventory(100)

        # Assert
        assert "Cannot subtract 100 items" in str(exc_info.value)

    def test_to_dict(self):
        # Arrange
        category = Mock(spec=CategoryEntity)
        category.to_dict.return_value = {"id": 1, "name": "Category"}
        price = Mock(spec=PriceEntity)
        price.to_dict.return_value = {"id": 1, "amount": 99.99}
        inventory = Mock(spec=InventoryEntity)
        inventory.to_dict.return_value = {"id": 1, "quantity": 100}
        product = ProductEntity(
            sku="ABC123",
            name="Product Name",
            description="Product Description",
            category=category,
            price=price,
            inventory=inventory,
            id=1,
            images=["https://example.com"],
        )

        # Act
        product_dict = product.to_dict()

        # Assert
        assert product_dict == {
            "id": 1,
            "sku": "ABC123",
            "name": "Product Name",
            "description": "Product Description",
            "category": {"id": 1, "name": "Category"},
            "price": {"id": 1, "amount": 99.99},
            "inventory": {"id": 1, "quantity": 100},
            "images": ["https://example.com"],
        }


if __name__ == "__main__":
    pytest.main()
