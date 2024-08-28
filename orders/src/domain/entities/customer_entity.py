import re
from typing import Optional

from src.domain.exceptions import InvalidEntity


class CustomerEntity:

    def __init__(
        self,
        name: str,
        email: str,
        phone_number: Optional[str] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.phone_number = phone_number

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        if value is not None and value <= 0:
            raise InvalidEntity("ID must be a positive integer.")
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or len(value) < 2:
            raise InvalidEntity("Name must be at least 2 characters long.")
        self._name = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, value):
            raise InvalidEntity("Invalid email format.")
        self._email = value

    @property
    def phone_number(self) -> Optional[str]:
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value: Optional[str]):
        if value:
            phone_number_regex = r"^\+\d{1,3}\d{1,14}$"
            if not re.match(phone_number_regex, value):
                raise InvalidEntity("Invalid phone number format.")
        self._phone_number = value

    def update_customer(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
    ):
        if name:
            self.name = name
        if email:
            self.email = email
        if phone_number:
            self.phone_number = phone_number

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
        }
