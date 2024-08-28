import os

import pika
from src.application.services.payment_service import PaymentService
from src.application.services.qr_code_service import QRCodeService
from src.infrastructure.health.health_service import HealthService
from src.infrastructure.messaging.payment_publisher import PaymentPublisher
from src.infrastructure.persistence.db_setup import db, payments_collection
from src.infrastructure.persistence.mongo_payment_repository import (
    MongoDBPaymentRepository,
)


def get_payment_service() -> PaymentService:
    payment_repository = MongoDBPaymentRepository(payments_collection)
    payment_publisher = get_payment_publisher()
    qr_code_service = get_qr_code_service()
    return PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )


def get_payment_publisher() -> PaymentPublisher:
    connection_params = pika.ConnectionParameters(
        host="rabbitmq", heartbeat=120
    )
    return PaymentPublisher(connection_params)


def get_qr_code_service() -> QRCodeService:
    mercado_pago_access_token = os.getenv(
        "MERCADO_PAGO_ACCESS_TOKEN", "your_access_token_here"
    )
    return QRCodeService(mercado_pago_access_token)


def get_health_service() -> HealthService:
    return HealthService(db, rabbitmq_host="rabbitmq")
