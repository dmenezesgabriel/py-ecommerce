import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.adapters.api import health_api, payment_api
from src.adapters.dependencies import get_payment_service
from src.infrastructure.messaging.order_subscriber import OrderSubscriber

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
    payment_service = get_payment_service()
    order_subscriber = OrderSubscriber(payment_service)
    threading.Thread(target=order_subscriber.start_consuming).start()
    yield


app = FastAPI(lifespan=lifespan, root_path="/payments")
app.include_router(payment_api.router)
app.include_router(health_api.router)
