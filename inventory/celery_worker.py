from typing import Optional

from celery import Celery
from celery.signals import worker_process_init
from inventory_service import (
    ProductService,
    SQLAlchemyCategoryRepository,
    SQLAlchemyProductRepository,
    get_db,
)
from sqlalchemy.orm import Session

# Celery configuration
celery_app = Celery("inventory_worker", broker="amqp://guest:guest@rabbitmq//")

# Initialize FastAPI dependency overrides
db_session: Optional[Session] = None


@worker_process_init.connect
def init_worker(**kwargs):
    global db_session
    db_session = next(get_db())


def get_product_service() -> ProductService:
    product_repository = SQLAlchemyProductRepository(db_session)
    category_repository = SQLAlchemyCategoryRepository(db_session)
    return ProductService(product_repository, category_repository)


@celery_app.task(name="inventory.add_quantity")
def add_quantity_task(sku: str, quantity: int):
    service = get_product_service()
    try:
        service.add_inventory(sku, quantity)
        return f"Added {quantity} to inventory for SKU: {sku}"
    except Exception as e:
        return str(e)


@celery_app.task(name="inventory.subtract_quantity")
def subtract_quantity_task(sku: str, quantity: int):
    service = get_product_service()
    try:
        service.subtract_inventory(sku, quantity)
        return f"Subtracted {quantity} from inventory for SKU: {sku}"
    except Exception as e:
        return str(e)
