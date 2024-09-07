import logging

from fastapi import FastAPI
from src.adapters.api import customer_api, delivery_api, health_api

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI(root_path="/delivery")
app.include_router(customer_api.router)
app.include_router(delivery_api.router)
app.include_router(health_api.router)
