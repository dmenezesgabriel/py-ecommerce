import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from src.domain.entities.category_entity import CategoryEntity
from src.domain.entities.inventory_entity import InventoryEntity
from src.domain.entities.price_entity import PriceEntity
from src.domain.entities.product_entity import ProductEntity
from src.domain.repositories.product_repository import ProductRepository
from src.infrastructure.persistence.models import (
    CategoryModel,
    InventoryModel,
    PriceModel,
    ProductModel,
)

logger = logging.getLogger("app")


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, product: ProductEntity) -> ProductEntity:

        category_model = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == product.category.name)
            .first()
        )
        if not category_model:
            category_model = CategoryModel(name=product.category.name)
            self.db.add(category_model)
            self.db.commit()
            self.db.refresh(category_model)

        if product.id:
            db_product = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product.id)
                .first()
            )
        else:
            db_product = ProductModel(
                sku=product.sku,
                name=product.name,
                category_id=category_model.id,
            )
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)

        db_product.name = product.name
        db_product.category = category_model
        db_product.price = PriceModel(
            product_id=db_product.id, amount=product.price.amount
        )
        db_product.inventory = InventoryModel(
            product_id=db_product.id, quantity=product.inventory.quantity
        )

        self.db.add(db_product.price)
        self.db.add(db_product.inventory)
        self.db.commit()
        self.db.refresh(db_product)
        return ProductEntity(
            id=db_product.id,
            sku=db_product.sku,
            name=db_product.name,
            category=CategoryEntity(
                name=db_product.category.name, id=db_product.category.id
            ),
            inventory=InventoryEntity(
                id=db_product.inventory.id,
                quantity=db_product.inventory.quantity,
            ),
            price=PriceEntity(
                id=db_product.price.id, amount=db_product.price.amount
            ),
        )

    def find_by_sku(self, sku: str) -> Optional[ProductEntity]:
        db_product = (
            self.db.query(ProductModel).filter(ProductModel.sku == sku).first()
        )
        if db_product:
            category = (
                self.db.query(CategoryModel)
                .filter(CategoryModel.id == db_product.category_id)
                .first()
            )
            return ProductEntity(
                id=db_product.id,
                sku=db_product.sku,
                name=db_product.name,
                category=CategoryEntity(id=category.id, name=category.name),
                price=PriceEntity(
                    id=db_product.price.id, amount=db_product.price.amount
                ),
                inventory=InventoryEntity(
                    id=db_product.inventory.id,
                    quantity=db_product.inventory.quantity,
                ),
            )
        return None

    def delete(self, product: ProductEntity):
        db_product = (
            self.db.query(ProductModel)
            .filter(ProductModel.sku == product.sku)
            .first()
        )
        if db_product:
            db_price = (
                self.db.query(PriceModel)
                .filter(PriceModel.product_id == db_product.id)
                .first()
            )
            db_inventory = (
                self.db.query(InventoryModel)
                .filter(InventoryModel.product_id == db_product.id)
                .first()
            )

            self.db.delete(db_inventory)
            self.db.delete(db_price)
            self.db.delete(db_product)
            self.db.commit()

    def list_all(self) -> List[ProductEntity]:
        db_products = self.db.query(ProductModel).all()
        return [
            ProductEntity(
                id=db_product.id,
                sku=db_product.sku,
                name=db_product.name,
                category=CategoryEntity(
                    id=db_product.category.id, name=db_product.category.name
                ),
                price=PriceEntity(
                    id=db_product.price.id, amount=db_product.price.amount
                ),
                inventory=InventoryEntity(
                    id=db_product.inventory.id,
                    quantity=db_product.inventory.quantity,
                ),
            )
            for db_product in db_products
        ]

    def find_by_category(
        self, category: CategoryEntity
    ) -> List[ProductEntity]:
        db_category = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == category.name)
            .first()
        )
        if db_category:
            db_products = (
                self.db.query(ProductModel)
                .filter(ProductModel.category_id == db_category.id)
                .all()
            )
            return [
                ProductEntity(
                    id=db_product.id,
                    sku=db_product.sku,
                    name=db_product.name,
                    category=CategoryEntity(
                        id=db_category.id, name=db_category.name
                    ),
                    price=PriceEntity(
                        id=db_product.price.id, amount=db_product.price.amount
                    ),
                    inventory=InventoryEntity(
                        id=db_product.inventory.id,
                        quantity=db_product.inventory.quantity,
                    ),
                )
                for db_product in db_products
            ]
        return []
