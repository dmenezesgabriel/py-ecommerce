from typing import Optional


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
