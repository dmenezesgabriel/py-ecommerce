import logging
import threading
from contextlib import asynccontextmanager

import pika
from fastapi import FastAPI
from src.adapters.api import customer_api, health_api, order_api
from src.adapters.dependencies import (
    get_inventory_publisher,
    get_order_update_publisher,
)
from src.application.services.order_service import OrderService
from src.infrastructure.messaging.delivery_subscriber import DeliverySubscriber
from src.infrastructure.messaging.payment_subscriber import PaymentSubscriber
from src.infrastructure.persistence.db_setup import SessionLocal
from src.infrastructure.persistence.sqlalchemy_customer_repository import (
    SQLAlchemyCustomerRepository,
)
from src.infrastructure.persistence.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository,
)

# Set up logging
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
    order_repository = SQLAlchemyOrderRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    inventory_publisher = get_inventory_publisher()
    order_update_publisher = get_order_update_publisher()
    order_service = OrderService(
        order_repository,
        customer_repository,
        inventory_publisher,
        order_update_publisher,
    )
    connection_params = pika.ConnectionParameters(
        host="rabbitmq", heartbeat=120
    )
    payment_subscriber = PaymentSubscriber(order_service, connection_params)
    delivery_subscriber = DeliverySubscriber(order_service, connection_params)
    threading.Thread(target=payment_subscriber.start_consuming).start()
    threading.Thread(target=delivery_subscriber.start_consuming).start()
    yield


app = FastAPI(lifespan=lifespan, root_path="/orders")
app.include_router(order_api.router)
app.include_router(customer_api.router)
app.include_router(health_api.router)
