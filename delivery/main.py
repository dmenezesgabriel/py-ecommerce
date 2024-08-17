from fastapi import FastAPI
from src.adapters.api import customer_api, delivery_api, health_api

app = FastAPI(root_path="/delivery")
app.include_router(customer_api.router)
app.include_router(delivery_api.router)
app.include_router(health_api.router)
