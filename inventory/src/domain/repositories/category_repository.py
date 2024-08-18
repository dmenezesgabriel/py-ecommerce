from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.category_entity import CategoryEntity


class CategoryRepository(ABC):
    @abstractmethod
    def save(self, category: CategoryEntity):
        raise NotImplementedError

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[CategoryEntity]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[CategoryEntity]:
        raise NotImplementedError
