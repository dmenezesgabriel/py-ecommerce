from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.customer_entity import CustomerEntity


class CustomerRepository(ABC):
    @abstractmethod
    def save(self, customer: CustomerEntity):
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[CustomerEntity]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[CustomerEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, customer: CustomerEntity):
        raise NotImplementedError
