from typing import List, Optional

from src.domain.entities.customer_entity import CustomerEntity


class CustomerRepository:
    def save(self, customer: CustomerEntity):
        raise NotImplementedError

    def find_by_email(self, email: str) -> Optional[CustomerEntity]:
        raise NotImplementedError

    def list_all(self) -> List[CustomerEntity]:
        raise NotImplementedError

    def delete(self, customer: CustomerEntity):
        raise NotImplementedError
