from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.product_entity import ProductEntity


class ProductRepository(ABC):
    @abstractmethod
    def save(self, product: ProductEntity):
        raise NotImplementedError

    @abstractmethod
    def find_by_sku(self, sku: str) -> Optional[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, product: ProductEntity):
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[ProductEntity]:
        raise NotImplementedError

    @abstractmethod
    def find_by_category(
        self, category: CategoryEntity
    ) -> List[ProductEntity]:
        raise NotImplementedError
