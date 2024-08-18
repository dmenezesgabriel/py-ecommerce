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
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+123456789",
                },
                {
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com",
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
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone_number": "+123456789",
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "phone_number": None,
                },
            ]
        }
