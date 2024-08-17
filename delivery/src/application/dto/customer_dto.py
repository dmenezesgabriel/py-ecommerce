from typing import Optional

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone_number: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Alice Smith",
                    "email": "alice.smith@example.com",
                    "phone_number": "+11234567890",
                },
                {
                    "name": "Bob Johnson",
                    "email": "bob.johnson@example.com",
                    "phone_number": None,
                },
            ]
        }


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {
                    "id": 1,
                    "name": "Alice Smith",
                    "email": "alice.smith@example.com",
                    "phone_number": "+11234567890",
                },
                {
                    "id": 2,
                    "name": "Bob Johnson",
                    "email": "bob.johnson@example.com",
                    "phone_number": None,
                },
            ]
        }
