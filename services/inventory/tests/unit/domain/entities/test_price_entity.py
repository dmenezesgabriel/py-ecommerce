import pytest
from src.domain.entities.price_entity import PriceEntity
from src.domain.exceptions import InvalidEntity


class TestPriceEntity:

    def test_create_valid_price(self):
        # Arrange & Act
        price = PriceEntity(amount=99.99, id=1)

        # Assert
        assert price.id == 1
        assert price.amount == 99.99

    def test_create_price_invalid_id(self):
        # Arrange & Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            PriceEntity(amount=99.99, id=-1)

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_create_price_invalid_amount(self):
        # Arrange & Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            PriceEntity(amount=-10.00, id=1)

        # Assert
        assert "Invalid amount" in str(exc_info.value)

    def test_set_valid_id(self):
        # Arrange
        price = PriceEntity(amount=99.99, id=1)

        # Act
        price.id = 2

        # Assert
        assert price.id == 2

    def test_set_invalid_id(self):
        # Arrange
        price = PriceEntity(amount=99.99, id=1)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            price.id = -1

        # Assert
        assert "Invalid id" in str(exc_info.value)

    def test_set_valid_amount(self):
        # Arrange
        price = PriceEntity(amount=99.99, id=1)

        # Act
        price.amount = 199.99

        # Assert
        assert price.amount == 199.99

    def test_set_invalid_amount(self):
        # Arrange
        price = PriceEntity(amount=99.99, id=1)

        # Act / Assert
        with pytest.raises(InvalidEntity) as exc_info:
            price.amount = -50.00

        # Assert
        assert "Invalid amount" in str(exc_info.value)

    def test_to_dict(self):
        # Arrange
        price = PriceEntity(amount=99.99, id=1)

        # Act
        price_dict = price.to_dict()

        # Assert
        assert price_dict == {"id": 1, "amount": 99.99}


if __name__ == "__main__":
    pytest.main()
