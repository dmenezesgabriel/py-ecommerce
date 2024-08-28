import pytest
from pydantic import ValidationError
from src.application.dto.inventory_dto import InventoryUpdate


class TestInventoryUpdate:

    def test_create_inventory_update_valid(self):
        # Arrange & Act
        inventory_update = InventoryUpdate(quantity=50)

        # Assert
        assert inventory_update.quantity == 50

    def test_create_inventory_update_invalid_quantity(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            InventoryUpdate(quantity="fifty")  # Invalid type

    def test_inventory_update_to_dict(self):
        # Arrange
        inventory_update = InventoryUpdate(quantity=100)

        # Act
        inventory_dict = inventory_update.model_dump()

        # Assert
        assert inventory_dict == {"quantity": 100}

    def test_inventory_update_example(self):
        # Arrange & Act
        example = InventoryUpdate.model_config["json_schema_extra"]["examples"]

        # Assert
        assert example == [
            {"quantity": 50},
            {"quantity": 200},
        ]


if __name__ == "__main__":
    pytest.main()
