from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from main import app, lifespan


@pytest.fixture
def mock_session():
    with patch("main.SessionLocal") as mock_session:
        yield mock_session


@pytest.fixture
def mock_order_repo():
    with patch("main.SQLAlchemyOrderRepository") as mock_order_repo:
        yield mock_order_repo


@pytest.fixture
def mock_customer_repo():
    with patch("main.SQLAlchemyCustomerRepository") as mock_customer_repo:
        yield mock_customer_repo


@pytest.fixture
def mock_inventory_publisher():
    with patch("main.get_inventory_publisher") as mock_inventory_publisher:
        yield mock_inventory_publisher


@pytest.fixture
def mock_order_update_publisher():
    with patch(
        "main.get_order_update_publisher"
    ) as mock_order_update_publisher:
        yield mock_order_update_publisher


@pytest.fixture
def mock_order_service():
    with patch("main.OrderService") as mock_order_service:
        yield mock_order_service


@pytest.fixture
def mock_pika_connection():
    with patch("main.pika.ConnectionParameters") as mock_pika_connection:
        yield mock_pika_connection


@pytest.fixture
def mock_payment_subscriber():
    with patch("main.PaymentSubscriber") as mock_payment_subscriber:
        yield mock_payment_subscriber


@pytest.fixture
def mock_delivery_subscriber():
    with patch("main.DeliverySubscriber") as mock_delivery_subscriber:
        yield mock_delivery_subscriber


@pytest.mark.asyncio
async def test_lifespan(
    mock_session,
    mock_order_repo,
    mock_customer_repo,
    mock_inventory_publisher,
    mock_order_update_publisher,
    mock_order_service,
    mock_pika_connection,
    mock_payment_subscriber,
    mock_delivery_subscriber,
):
    test_app = FastAPI(lifespan=lifespan)

    async with lifespan(test_app):
        # Assert that the session was initialized
        mock_session.assert_called_once()

        # Assert that repositories were initialized
        mock_order_repo.assert_called_once_with(mock_session())
        mock_customer_repo.assert_called_once_with(mock_session())

        # Assert that publishers were initialized
        mock_inventory_publisher.assert_called_once()
        mock_order_update_publisher.assert_called_once()

        # Assert that the order service was initialized with correct arguments
        mock_order_service.assert_called_once_with(
            mock_order_repo(),
            mock_customer_repo(),
            mock_inventory_publisher(),
            mock_order_update_publisher(),
        )

        # Assert that the pika connection was initialized
        mock_pika_connection.assert_called_once_with(
            host="rabbitmq", heartbeat=120
        )

        # Assert that subscribers were initialized and started
        mock_payment_subscriber.assert_called_once_with(
            mock_order_service(), mock_pika_connection()
        )
        mock_delivery_subscriber.assert_called_once_with(
            mock_order_service(), mock_pika_connection()
        )

        # Verify that the start_consuming method was called in separate threads
        assert mock_payment_subscriber().start_consuming.call_count == 1
        assert mock_delivery_subscriber().start_consuming.call_count == 1


def test_app_routes():
    routes = [route.path for route in app.router.routes]

    assert "/orders/" in routes
    assert "/orders/{order_id}" in routes
    assert "/customers/" in routes
    assert "/health" in routes
