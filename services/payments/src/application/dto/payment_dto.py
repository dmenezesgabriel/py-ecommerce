from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel
from src.domain.entities.payment_entity import PaymentStatus


class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    status: PaymentStatus

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_id": 1,
                    "amount": 100.00,
                    "status": "pending",
                },
                {
                    "order_id": 2,
                    "amount": 250.75,
                    "status": "completed",
                },
            ]
        }
    }


class PaymentUpdate(BaseModel):
    order_id: int
    amount: float
    status: PaymentStatus

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_id": 1,
                    "amount": 100.00,
                    "status": "completed",
                },
                {
                    "order_id": 2,
                    "amount": 250.75,
                    "status": "failed",
                },
            ]
        }
    }


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "completed"},
                {"status": "canceled"},
            ]
        }
    }


class PaymentResponse(BaseModel):
    id: str
    order_id: int
    amount: float
    status: PaymentStatus
    qr_code: Optional[str]
    qr_code_expiration: Optional[int]

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,
        },
        "json_schema_extra": {
            "examples": [
                {
                    "id": "64c8cbe2f3a5e9a1c4b63e29",
                    "order_id": 1,
                    "amount": 100.00,
                    "status": "completed",
                    "qr_code": "https://www.mercadopago.com.br/qr-code/1",
                    "qr_code_expiration": 1633520400,
                },
                {
                    "id": "64c8cbe2f3a5e9a1c4b63e30",
                    "order_id": 2,
                    "amount": 250.75,
                    "status": "pending",
                    "qr_code": "https://www.mercadopago.com.br/qr-code/2",
                    "qr_code_expiration": 1633520400,
                },
            ]
        },
    }


class WebhookPayload(BaseModel):
    payment_id: str
    status: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "payment_id": "64c8cbe2f3a5e9a1c4b63e29",
                    "status": "approved",
                },
                {
                    "payment_id": "64c8cbe2f3a5e9a1c4b63e30",
                    "status": "rejected",
                },
            ]
        }
    }
