from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.order_entity import OrderEntity


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: OrderEntity):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[OrderEntity]:
        raise NotImplementedError

    @abstractmethod
    def find_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, order: OrderEntity):
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[OrderEntity]:
        raise NotImplementedError
