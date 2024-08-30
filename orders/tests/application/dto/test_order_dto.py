import pytest
from pydantic import ValidationError
from src.application.dto.customer_dto import CustomerResponse
from src.application.dto.order_dto import (
    EstimatedTimeUpdate,
    OrderCreate,
    OrderResponse,
    OrdersPaginatedResponse,
    OrderStatusUpdate,
    PaginationMeta,
)
from src.application.dto.order_item_dto import OrderItemResponse
from src.domain.entities.order_entity import OrderStatus


def test_order_create_valid():
    order_data = {
        "customer": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "+123456789",
        },
        "order_items": [
            {"product_sku": "ABC123", "quantity": 2},
            {"product_sku": "XYZ456", "quantity": 1},
        ],
    }
    order = OrderCreate(**order_data)

    assert order.customer.name == "John Doe"
    assert len(order.order_items) == 2


def test_order_create_invalid_missing_customer():
    order_data = {
        "order_items": [
            {"product_sku": "ABC123", "quantity": 2},
            {"product_sku": "XYZ456", "quantity": 1},
        ],
    }

    with pytest.raises(ValidationError):
        OrderCreate(**order_data)


def test_order_status_update_valid():
    order_status_data = {"status": OrderStatus.CONFIRMED}
    order_status_update = OrderStatusUpdate(**order_status_data)

    assert order_status_update.status == OrderStatus.CONFIRMED


def test_order_status_update_invalid():
    order_status_data = {"status": "invalid_status"}

    with pytest.raises(ValidationError):
        OrderStatusUpdate(**order_status_data)


def test_order_response_valid():
    order_data = {
        "id": 1,
        "order_number": "ORD123",
        "customer": {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "+123456789",
        },
        "order_items": [
            {
                "product_sku": "ABC123",
                "quantity": 2,
                "name": "Product A",
                "description": "Product A description",
                "price": 10.0,
            },
            {
                "product_sku": "XYZ456",
                "quantity": 1,
                "name": "Product B",
                "description": "Product B description",
                "price": 20.0,
            },
        ],
        "status": OrderStatus.CONFIRMED,
        "total_amount": 30.00,
        "estimated_time": "02:30",
    }

    order = OrderResponse(**order_data)

    assert order.id == 1
    assert order.customer.name == "John Doe"
    assert order.order_items[0].product_sku == "ABC123"
    assert order.total_amount == 30.00


def test_estimated_time_update_valid():
    estimated_time_data = {"estimated_time": "02:30"}
    estimated_time_update = EstimatedTimeUpdate(**estimated_time_data)

    assert estimated_time_update.estimated_time == "02:30"


def test_estimated_time_update_invalid():
    estimated_time_data = {
        "estimated_time": 230
    }  # Invalid, should be a string

    with pytest.raises(ValidationError):
        EstimatedTimeUpdate(**estimated_time_data)


def test_orders_paginated_response_valid():
    pagination_data = {
        "current_page": 1,
        "records_per_page": 1,
        "number_of_pages": 5,
        "total_records": 5,
    }
    orders_data = {
        "orders": [
            {
                "id": 1,
                "order_number": "ORD123",
                "customer": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+123456789",
                },
                "order_items": [
                    {
                        "product_sku": "ABC123",
                        "quantity": 2,
                        "name": "Product A",
                        "description": "Product A description",
                        "price": 10.0,
                    },
                ],
                "status": OrderStatus.CONFIRMED,
                "total_amount": 30.00,
                "estimated_time": "02:30",
            }
        ],
        "pagination": pagination_data,
    }

    orders_paginated_response = OrdersPaginatedResponse(**orders_data)

    assert len(orders_paginated_response.orders) == 1
    assert orders_paginated_response.pagination.current_page == 1


def test_orders_paginated_response_invalid():
    pagination_data = {
        "current_page": 1,
        "records_per_page": 1,
        "number_of_pages": 5,
    }  # Missing total_records

    orders_data = {
        "orders": [
            {
                "id": 1,
                "order_number": "ORD123",
                "customer": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+123456789",
                },
                "order_items": [
                    {
                        "product_sku": "ABC123",
                        "quantity": 2,
                        "name": "Product A",
                        "description": "Product A description",
                        "price": 10.0,
                    },
                ],
                "status": OrderStatus.CONFIRMED,
                "total_amount": 30.00,
                "estimated_time": "02:30",
            }
        ],
        "pagination": pagination_data,
    }

    with pytest.raises(ValidationError):
        OrdersPaginatedResponse(**orders_data)


def test_pagination_meta_valid():
    pagination_meta_data = {
        "current_page": 1,
        "records_per_page": 10,
        "number_of_pages": 5,
        "total_records": 50,
    }
    pagination_meta = PaginationMeta(**pagination_meta_data)

    assert pagination_meta.current_page == 1
    assert pagination_meta.records_per_page == 10
    assert pagination_meta.number_of_pages == 5
    assert pagination_meta.total_records == 50


def test_pagination_meta_invalid():
    pagination_meta_data = {
        "current_page": 1,
        "records_per_page": "ten",  # Invalid, should be an integer
        "number_of_pages": 5,
        "total_records": 50,
    }

    with pytest.raises(ValidationError):
        PaginationMeta(**pagination_meta_data)
