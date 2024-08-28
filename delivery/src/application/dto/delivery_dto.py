from pydantic import BaseModel
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse
from src.domain.entities.delivery_entity import DeliveryStatus


class AddressCreate(BaseModel):
    city: str
    state: str
    country: str
    zip_code: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "city": "New York",
                    "state": "NY",
                    "country": "USA",
                    "zip_code": "10001",
                },
                {
                    "city": "Los Angeles",
                    "state": "CA",
                    "country": "USA",
                    "zip_code": "90001",
                },
            ]
        }
    }


class DeliveryCreate(BaseModel):
    order_id: int
    delivery_address: str
    delivery_date: str
    status: DeliveryStatus
    address: AddressCreate
    customer: CustomerCreate

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_id": 123,
                    "delivery_address": "123 Main St, Apt 4B",
                    "delivery_date": "2024-08-20",
                    "status": "pending",
                    "address": {
                        "city": "New York",
                        "state": "NY",
                        "country": "USA",
                        "zip_code": "10001",
                    },
                    "customer": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone_number": "+123456789",
                    },
                }
            ]
        }
    }


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "in_transit"},
                {"status": "delivered"},
            ]
        }
    }


class AddressResponse(BaseModel):
    id: int
    city: str
    state: str
    country: str
    zip_code: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "city": "New York",
                    "state": "NY",
                    "country": "USA",
                    "zip_code": "10001",
                },
                {
                    "id": 2,
                    "city": "Los Angeles",
                    "state": "CA",
                    "country": "USA",
                    "zip_code": "90001",
                },
            ]
        },
    }


class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    delivery_address: str
    delivery_date: str
    status: DeliveryStatus
    address: AddressResponse
    customer: CustomerResponse

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "order_id": 123,
                    "delivery_address": "123 Main St, Apt 4B",
                    "delivery_date": "2024-08-20",
                    "status": "pending",
                    "address": {
                        "id": 1,
                        "city": "New York",
                        "state": "NY",
                        "country": "USA",
                        "zip_code": "10001",
                    },
                    "customer": {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone_number": "+123456789",
                    },
                }
            ]
        },
    }
