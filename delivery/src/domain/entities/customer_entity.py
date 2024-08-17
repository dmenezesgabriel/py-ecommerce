from typing import Optional


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
