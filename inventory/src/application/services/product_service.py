import logging
from typing import List, Optional

from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.inventory_entity import InventoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.entities.product_entity import ProductEntity
from src.domain.exceptions import EntityAlreadyExists, EntityNotFound
from src.domain.repositories.category_repository import CategoryRepository
from src.domain.repositories.product_repository import ProductRepository

logger = logging.getLogger("app")


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository

    def create_product(
        self,
        sku: str,
        name: str,
        category_name: str,
        price: float,
        quantity: int,
        description: Optional[str] = None,
        images: Optional[List[str]] = None,
    ) -> ProductEntity:
        category = self.category_repository.find_by_name(category_name)
        if not category:
            category = CategoryEntity(name=category_name)
            self.category_repository.save(category)

        product = self.product_repository.find_by_sku(sku)
        if product:
            raise EntityAlreadyExists(
                f"Product with SKU '{sku}' already exists"
            )

        price_entity = PriceEntity(amount=price)
        inventory_entity = InventoryEntity(quantity=quantity)
        product = ProductEntity(
            sku=sku,
            name=name,
            category=category,
            price=price_entity,
            inventory=inventory_entity,
            description=description,
            images=images,
        )
        new_product = self.product_repository.save(product)
        return new_product

    def get_product_by_sku(self, sku: str) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")
        return product

    def update_product(
        self,
        sku: str,
        name: str,
        category_name: str,
        price: float,
        quantity: int,
        description: Optional[str] = None,
        images: Optional[List[str]] = None,
    ) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        category = self.category_repository.find_by_name(category_name)
        if not category:
            category = CategoryEntity(name=category_name)
            self.category_repository.save(category)

        product.name = name
        product.category = category
        product.set_price(price)
        product.set_inventory(quantity)
        product.description = description
        product.images = images or []
        updated_product = self.product_repository.save(product)
        return updated_product

    def delete_product(self, sku: str) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        self.product_repository.delete(product)
        return product

    def list_products(self) -> List[ProductEntity]:
        return self.product_repository.list_all()

    def get_products_by_category(
        self, category_name: str
    ) -> List[ProductEntity]:
        category = self.category_repository.find_by_name(category_name)
        if not category:
            raise EntityNotFound(f"Category '{category_name}' not found")
        return self.product_repository.find_by_category(category)

    def add_inventory(self, sku: str, quantity: int) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        product.add_inventory(quantity)
        self.product_repository.save(product)
        return product

    def subtract_inventory(self, sku: str, quantity: int) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        product.subtract_inventory(quantity)
        self.product_repository.save(product)
        return product

    def create_category(self, name: str) -> CategoryEntity:
        category = self.category_repository.find_by_name(name)
        if category:
            raise EntityAlreadyExists(
                f"Category with name '{name}' already exists"
            )
        category = CategoryEntity(name=name)
        self.category_repository.save(category)
        return category

    def list_categories(self) -> List[CategoryEntity]:
        return self.category_repository.list_all()

    def list_products_paginated(
        self, current_page: int, records_per_page: int
    ):
        (
            products,
            current_page,
            records_per_page,
            number_of_pages,
            total_records,
        ) = self.product_repository.list_all_paginated(
            current_page, records_per_page
        )
        return (
            products,
            current_page,
            records_per_page,
            number_of_pages,
            total_records,
        )

    def list_categories_paginated(
        self, current_page: int, records_per_page: int
    ):
        (
            categories,
            current_page,
            records_per_page,
            number_of_pages,
            total_records,
        ) = self.category_repository.list_all_paginated(
            current_page, records_per_page
        )
        return (
            categories,
            current_page,
            records_per_page,
            number_of_pages,
            total_records,
        )
