import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.adapters.api import (
    category_api,
    health_api,
    inventory_api,
    product_api,
)
from src.application.services.product_service import ProductService
from src.infrastructure.messaging.inventory_subscriber import (
    InventorySubscriber,
)
from src.infrastructure.persistence.db_setup import SessionLocal
from src.infrastructure.persistence.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from src.infrastructure.persistence.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    product_repository = SQLAlchemyProductRepository(db)
    category_repository = SQLAlchemyCategoryRepository(db)
    product_service = ProductService(product_repository, category_repository)

    inventory_subscriber = InventorySubscriber(product_service)
    threading.Thread(target=inventory_subscriber.start_consuming).start()
    yield


app = FastAPI(lifespan=lifespan, root_path="/inventory")
app.include_router(category_api.router)
app.include_router(product_api.router)
app.include_router(inventory_api.router)
app.include_router(health_api.router)
