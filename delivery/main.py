from fastapi import FastAPI
from src.adapters.api import customer_api, delivery_api, health_api
from src.infrastructure.persistence.db_setup import Base, engine

app = FastAPI(root_path="/delivery")


@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


app.include_router(customer_api.router)
app.include_router(delivery_api.router)
app.include_router(health_api.router)
