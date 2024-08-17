from typing import Optional

from src.domain.exceptions import InvalidEntity


class AddressEntity:

    def __init__(
        self,
        city: str,
        state: str,
        country: str,
        zip_code: str,
        id: Optional[int] = None,
    ):
        self.id = id
        self.city = city
        self.state = state
        self.country = country
        self.zip_code = zip_code

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        if value is not None and value <= 0:
            raise InvalidEntity("ID must be a positive integer.")
        self._id = value

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str):
        if not value or len(value) < 2:
            raise InvalidEntity("City must be at least 2 characters long.")
        self._city = value

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str):
        if not value or len(value) < 2:
            raise InvalidEntity("State must be at least 2 characters long.")
        self._state = value

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, value: str):
        if not value or len(value) < 2:
            raise InvalidEntity("Country must be at least 2 characters long.")
        self._country = value

    @property
    def zip_code(self) -> str:
        return self._zip_code

    @zip_code.setter
    def zip_code(self, value: str):
        if not value or not value.isdigit() or len(value) not in (5, 9):
            raise InvalidEntity("Zip code must be a 5 or 9 digit number.")
        self._zip_code = value

    def update_address(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        zip_code: Optional[str] = None,
    ):
        if city:
            self.city = city
        if state:
            self.state = state
        if country:
            self.country = country
        if zip_code:
            self.zip_code = zip_code

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zip_code": self.zip_code,
        }
