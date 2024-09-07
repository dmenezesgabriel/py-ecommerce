import unittest

from src.domain.entities.address_entity import AddressEntity
from src.domain.exceptions import InvalidEntity


class TestAddressEntity(unittest.TestCase):

    def test_address_entity_creation_success(self):
        # Arrange
        city = "New York"
        state = "NY"
        country = "USA"
        zip_code = "10001"

        # Act
        address = AddressEntity(
            city=city, state=state, country=country, zip_code=zip_code
        )

        # Assert
        self.assertEqual(address.city, city)
        self.assertEqual(address.state, state)
        self.assertEqual(address.country, country)
        self.assertEqual(address.zip_code, zip_code)

    def test_address_entity_creation_invalid_city(self):
        # Arrange
        city = "N"
        state = "NY"
        country = "USA"
        zip_code = "10001"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            AddressEntity(
                city=city, state=state, country=country, zip_code=zip_code
            )
        self.assertEqual(
            str(context.exception), "City must be at least 2 characters long."
        )

    def test_address_entity_creation_invalid_state(self):
        # Arrange
        city = "New York"
        state = "N"
        country = "USA"
        zip_code = "10001"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            AddressEntity(
                city=city, state=state, country=country, zip_code=zip_code
            )
        self.assertEqual(
            str(context.exception), "State must be at least 2 characters long."
        )

    def test_address_entity_creation_invalid_country(self):
        # Arrange
        city = "New York"
        state = "NY"
        country = "U"
        zip_code = "10001"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            AddressEntity(
                city=city, state=state, country=country, zip_code=zip_code
            )
        self.assertEqual(
            str(context.exception),
            "Country must be at least 2 characters long.",
        )

    def test_address_entity_creation_invalid_zip_code(self):
        # Arrange
        city = "New York"
        state = "NY"
        country = "USA"
        zip_code = "1234"

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            AddressEntity(
                city=city, state=state, country=country, zip_code=zip_code
            )
        self.assertEqual(
            str(context.exception), "Zip code must be a 5 or 9 digit number."
        )

    def test_address_entity_creation_invalid_id(self):
        # Arrange
        city = "New York"
        state = "NY"
        country = "USA"
        zip_code = "10001"
        invalid_id = -1

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            AddressEntity(
                city=city,
                state=state,
                country=country,
                zip_code=zip_code,
                id=invalid_id,
            )
        self.assertEqual(
            str(context.exception), "ID must be a positive integer."
        )

    def test_address_entity_update_success(self):
        # Arrange
        address = AddressEntity(
            city="New York", state="NY", country="USA", zip_code="10001"
        )

        # Act
        address.update_address(
            city="Los Angeles", state="CA", zip_code="90001"
        )

        # Assert
        self.assertEqual(address.city, "Los Angeles")
        self.assertEqual(address.state, "CA")
        self.assertEqual(address.country, "USA")
        self.assertEqual(address.zip_code, "90001")

    def test_address_entity_update_invalid_country(self):
        # Arrange
        address = AddressEntity(
            city="New York", state="NY", country="USA", zip_code="10001"
        )

        # Act & Assert
        with self.assertRaises(InvalidEntity) as context:
            address.update_address(country="U")
        self.assertEqual(
            str(context.exception),
            "Country must be at least 2 characters long.",
        )

    def test_address_entity_to_dict(self):
        # Arrange
        address = AddressEntity(
            city="New York", state="NY", country="USA", zip_code="10001"
        )

        # Act
        address_dict = address.to_dict()

        # Assert
        expected_dict = {
            "id": None,
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "zip_code": "10001",
        }
        self.assertEqual(address_dict, expected_dict)


if __name__ == "__main__":
    unittest.main()
