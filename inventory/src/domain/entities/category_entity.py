from typing import Optional

from src.domain.exceptions import InvalidEntity


class CategoryEntity:
    def __init__(self, name: str, id: Optional[int] = None):
        self._id = id
        self._name = name
        self._validate_id(self._id)
        self._validate_name(self._name)

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: Optional[int]):
        self._validate_id(value)
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._validate_name(value)
        self._name = value

    def _validate_id(self, id_value: Optional[int]):
        if id_value is not None and (
            not isinstance(id_value, int) or id_value <= 0
        ):
            raise InvalidEntity(
                f"Invalid id: {id_value}. ID must be a positive integer or None."
            )

    def _validate_name(self, name_value: str):
        if not isinstance(name_value, str) or not name_value.strip():
            raise InvalidEntity(
                f"Invalid name: {name_value}. Name must be a non-empty string."
            )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "name": self._name,
        }
