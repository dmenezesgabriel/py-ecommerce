import pika
from fastapi import Depends
from sqlalchemy.orm import Session
from src.application.services.order_service import OrderService
from src.infrastructure.health.health_service import HealthService
from src.infrastructure.messaging.inventory_publisher import InventoryPublisher
from src.infrastructure.messaging.order_update_publisher import (
    OrderUpdatePublisher,
)
from src.infrastructure.persistence.db_setup import get_db
from src.infrastructure.persistence.sqlalchemy_customer_repository import (
    SQLAlchemyCustomerRepository,
)
from src.infrastructure.persistence.sqlalchemy_order_repository import (
    SQLAlchemyOrderRepository,
)


def get_health_service(
    db: Session = Depends(get_db),
) -> HealthService:
    return HealthService(db, rabbitmq_host="rabbitmq")


def get_inventory_publisher() -> (
    InventoryPublisher
):  # TODO this should be an interface
    connection_params = pika.ConnectionParameters(
        host="rabbitmq", heartbeat=120
    )
    return InventoryPublisher(connection_params)


def get_order_update_publisher() -> (
    OrderUpdatePublisher
):  # TODO this should be an interface
    connection_params = pika.ConnectionParameters(
        host="rabbitmq", heartbeat=120
    )
    return OrderUpdatePublisher(connection_params)


def get_order_service(
    db: Session = Depends(get_db),
    inventory_publisher: InventoryPublisher = Depends(get_inventory_publisher),
    order_update_publisher: OrderUpdatePublisher = Depends(
        get_order_update_publisher
    ),
) -> OrderService:
    order_repository = SQLAlchemyOrderRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    return OrderService(
        order_repository,
        customer_repository,
        inventory_publisher,
        order_update_publisher,
    )
