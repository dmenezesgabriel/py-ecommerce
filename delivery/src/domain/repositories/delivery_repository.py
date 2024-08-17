from typing import List, Optional

from src.domain.entities.delivery_entity import DeliveryEntity


class DeliveryRepository:
    def save(self, delivery: DeliveryEntity):
        raise NotImplementedError

    def find_by_id(self, delivery_id: int) -> Optional[DeliveryEntity]:
        raise NotImplementedError

    def find_by_order_id(self, order_id: int) -> Optional[DeliveryEntity]:
        raise NotImplementedError

    def delete(self, delivery: DeliveryEntity):
        raise NotImplementedError

    def list_all(self) -> List[DeliveryEntity]:
        raise NotImplementedError
