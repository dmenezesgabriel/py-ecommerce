from typing import Optional


class CategoryEntity:
    def __init__(self, name: str, id: Optional[int] = None):
        self.id = id
        self.name = name
