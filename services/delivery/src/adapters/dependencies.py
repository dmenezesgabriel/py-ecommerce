import pika
from fastapi import Depends
from sqlalchemy.orm import Session
from src.application.services.delivery_service import DeliveryService
from src.application.services.order_verification_service import (
    OrderVerificationService,
)
from src.config import Config
from src.infrastructure.health.health_service import HealthService
from src.infrastructure.messaging.delivery_publisher import DeliveryPublisher
from src.infrastructure.persistence.db_setup import get_db
from src.infrastructure.persistence.sqlalchemy_customer_repository import (
    SQLAlchemyCustomerRepository,
)
from src.infrastructure.persistence.sqlalchemy_delivery_repository import (
    SQLAlchemyDeliveryRepository,
)


def get_health_service(
    db: Session = Depends(get_db),
) -> HealthService:
    return HealthService(db, rabbitmq_host=Config.BROKER_HOST)


def get_delivery_service(
    db: Session = Depends(get_db),
    delivery_publisher: DeliveryPublisher = Depends(
        lambda: DeliveryPublisher(
            pika.ConnectionParameters(host=Config.BROKER_HOST, heartbeat=120)
        )
    ),
    order_verification_service: OrderVerificationService = Depends(
        OrderVerificationService
    ),
) -> DeliveryService:
    delivery_repository = SQLAlchemyDeliveryRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    return DeliveryService(
        delivery_repository,
        customer_repository,
        delivery_publisher,
        order_verification_service,
    )
