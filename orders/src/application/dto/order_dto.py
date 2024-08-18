from typing import List

from pydantic import BaseModel
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse
from src.application.dto.order_item_dto import (
    OrderItemCreate,
    OrderItemResponse,
)
from src.domain.entities.order_entity import OrderStatus


class OrderCreate(BaseModel):
    customer: CustomerCreate
    order_items: List[OrderItemCreate] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone_number": "+123456789",
                    },
                    "order_items": [
                        {"product_sku": "ABC123", "quantity": 2},
                        {"product_sku": "XYZ456", "quantity": 1},
                    ],
                },
                {
                    "customer": {
                        "name": "Jane Smith",
                        "email": "jane.smith@example.com",
                        "phone_number": None,
                    },
                    "order_items": [
                        {"product_sku": "LMN789", "quantity": 3},
                    ],
                },
            ]
        }
    }


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "confirmed",
                },
                {
                    "status": "paid",
                },
            ]
        }
    }


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer: CustomerResponse
    order_items: List[OrderItemResponse]
    status: OrderStatus
    total_amount: float

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
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
                        {"product_sku": "ABC123", "quantity": 2},
                        {"product_sku": "XYZ456", "quantity": 1},
                    ],
                    "status": "confirmed",
                    "total_amount": 30.00,
                }
            ]
        },
    }
