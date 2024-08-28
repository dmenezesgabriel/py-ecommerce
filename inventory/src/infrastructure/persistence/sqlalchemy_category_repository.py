import logging
from typing import List, Optional

from sqlalchemy.orm import Session
from src.domain.entities.category_entity import CategoryEntity
from src.domain.repositories.category_repository import CategoryRepository
from src.infrastructure.persistence.models import CategoryModel

logger = logging.getLogger("app")


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, category: CategoryEntity):
        db_category = CategoryModel(name=category.name)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        category.id = db_category.id

    def find_by_name(self, name: str) -> Optional[CategoryEntity]:
        db_category = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == name)
            .first()
        )
        if db_category:
            return CategoryEntity(id=db_category.id, name=db_category.name)
        return None

    def list_all(self) -> List[CategoryEntity]:
        db_categories = self.db.query(CategoryModel).all()
        return [
            CategoryEntity(id=db_category.id, name=db_category.name)
            for db_category in db_categories
        ]

    def list_all_paginated(self, current_page: int, records_per_page: int):
        offset = (current_page - 1) * records_per_page
        query = self.db.query(CategoryModel)

        total_records = query.count()  # Get the total number of records
        db_categories = (
            query.limit(records_per_page).offset(offset).all()
        )  # Apply limit and offset

        categories = [
            CategoryEntity(id=db_category.id, name=db_category.name)
            for db_category in db_categories
        ]

        number_of_pages = (
            total_records + records_per_page - 1
        ) // records_per_page

        logger.info(
            categories,
            current_page,
            records_per_page,
            number_of_pages,
            total_records,
        )
        return (
            categories,
            current_page,
            records_per_page,
            number_of_pages,
            total_records,
        )
