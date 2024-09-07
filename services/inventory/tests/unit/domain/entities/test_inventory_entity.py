import pytest
from src.domain.entities.inventory_entity import InventoryEntity
from src.domain.exceptions import InvalidEntity


class TestInventoryEntity:

    def test_create_valid_inventory(self):
        # Arrange & Act
        inventory = InventoryEntity(quantity=100, id=1)

        # Assert
        assert inventory.id == 1
        assert inventory.quantity == 100

    def test_create_inventory_invalid_id(self):
        # Arrange & Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            InventoryEntity(quantity=100, id=-1)

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_create_inventory_invalid_quantity(self):
        # Arrange & Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            InventoryEntity(quantity=-10, id=1)

        # Assert
        assert "Invalid quantity" in str(exc_info.value)

    def test_set_valid_id(self):
        # Arrange
        inventory = InventoryEntity(quantity=100, id=1)

        # Act
        inventory.id = 2

        # Assert
        assert inventory.id == 2

    def test_set_invalid_id(self):
        # Arrange
        inventory = InventoryEntity(quantity=100, id=1)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            inventory.id = -1

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_set_valid_quantity(self):
        # Arrange
        inventory = InventoryEntity(quantity=100, id=1)

        # Act
        inventory.quantity = 200

        # Assert
        assert inventory.quantity == 200

    def test_set_invalid_quantity(self):
        # Arrange
        inventory = InventoryEntity(quantity=100, id=1)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            inventory.quantity = -50

        # Assert
        assert "Invalid quantity" in str(exc_info.value)

    def test_set_quantity_method(self):
        # Arrange
        inventory = InventoryEntity(quantity=100, id=1)

        # Act
        inventory.set_quantity(150)

        # Assert
        assert inventory.quantity == 150

    def test_to_dict(self):
        # Arrange
        inventory = InventoryEntity(quantity=100, id=1)

        # Act
        inventory_dict = inventory.to_dict()

        # Assert
        assert inventory_dict == {"id": 1, "quantity": 100}


if __name__ == "__main__":
    pytest.main()
