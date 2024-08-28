from fastapi import Depends
from sqlalchemy.orm import Session
from src.application.services.product_service import ProductService
from src.config import Config
from src.infrastructure.health.health_service import HealthService
from src.infrastructure.persistence.db_setup import get_db
from src.infrastructure.persistence.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from src.infrastructure.persistence.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)


def get_health_service(db: Session = Depends(get_db)) -> HealthService:
    return HealthService(db, rabbitmq_host=Config.BROKER_HOST)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repository = SQLAlchemyProductRepository(db)
    category_repository = SQLAlchemyCategoryRepository(db)
    return ProductService(product_repository, category_repository)
