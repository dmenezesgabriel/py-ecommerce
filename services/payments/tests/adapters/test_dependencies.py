from unittest.mock import MagicMock, patch

import pika
import pytest
from src.adapters.dependencies import (
    get_health_service,
    get_payment_publisher,
    get_payment_service,
    get_qr_code_service,
)
from src.application.services.payment_service import PaymentService
from src.application.services.qr_code_service import QRCodeService
from src.infrastructure.health.health_service import HealthService
from src.infrastructure.messaging.payment_publisher import PaymentPublisher
from src.infrastructure.persistence.mongo_payment_repository import (
    MongoDBPaymentRepository,
)


@patch("src.adapters.dependencies.payments_collection")
@patch("src.adapters.dependencies.MongoDBPaymentRepository")
@patch("src.adapters.dependencies.get_payment_publisher")
@patch("src.adapters.dependencies.get_qr_code_service")
def test_get_payment_service(
    mock_qr_code_service,
    mock_payment_publisher,
    mock_mongo_repo,
    mock_payments_collection,
):
    mock_payment_repo_instance = MagicMock(spec=MongoDBPaymentRepository)
    mock_mongo_repo.return_value = mock_payment_repo_instance
    mock_qr_code_service_instance = MagicMock(spec=QRCodeService)
    mock_qr_code_service.return_value = mock_qr_code_service_instance
    mock_payment_publisher_instance = MagicMock(spec=PaymentPublisher)
    mock_payment_publisher.return_value = mock_payment_publisher_instance

    payment_service = get_payment_service()

    mock_mongo_repo.assert_called_once_with(mock_payments_collection)
    mock_qr_code_service.assert_called_once()
    mock_payment_publisher.assert_called_once()
    assert isinstance(payment_service, PaymentService)
    assert payment_service.payment_repository == mock_mongo_repo.return_value
    assert payment_service.qr_code_service == mock_qr_code_service_instance
    assert payment_service.payment_publisher == mock_payment_publisher_instance


@patch("src.adapters.dependencies.pika.ConnectionParameters", autospec=True)
@patch("src.adapters.dependencies.PaymentPublisher")
def test_get_payment_publisher(
    mock_payment_publisher, mock_connection_parameters
):
    mock_connection_params_instance = mock_connection_parameters.return_value
    mock_payment_publisher_instance = MagicMock(spec=PaymentPublisher)
    mock_payment_publisher.return_value = mock_payment_publisher_instance

    payment_publisher = get_payment_publisher()

    mock_connection_parameters.assert_called_once_with(
        host="rabbitmq", heartbeat=120
    )
    mock_payment_publisher.assert_called_once_with(
        mock_connection_params_instance
    )
    assert payment_publisher == mock_payment_publisher_instance


@patch("src.adapters.dependencies.os.getenv")
@patch("src.adapters.dependencies.QRCodeService")
def test_get_qr_code_service(mock_qr_code_service, mock_getenv):
    mock_getenv.return_value = "fake_access_token"
    mock_qr_code_service_instance = MagicMock(spec=QRCodeService)
    mock_qr_code_service.return_value = mock_qr_code_service_instance

    qr_code_service = get_qr_code_service()

    mock_getenv.assert_called_once_with(
        "MERCADO_PAGO_ACCESS_TOKEN", "your_access_token_here"
    )
    mock_qr_code_service.assert_called_once_with("fake_access_token")
    assert qr_code_service == mock_qr_code_service_instance
