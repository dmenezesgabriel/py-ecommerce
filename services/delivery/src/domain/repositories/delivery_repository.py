from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.delivery_entity import DeliveryEntity


class DeliveryRepository(ABC):
    @abstractmethod
    def save(self, delivery: DeliveryEntity):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, delivery_id: int) -> Optional[DeliveryEntity]:
        raise NotImplementedError

    @abstractmethod
    def find_by_order_id(self, order_id: int) -> Optional[DeliveryEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, delivery: DeliveryEntity):
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[DeliveryEntity]:
        raise NotImplementedError
