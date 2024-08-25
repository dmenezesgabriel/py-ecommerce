from typing import List, Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    category_name: str
    price: float
    quantity: int
    description: Optional[str] = None  # Add description
    images: Optional[List[str]] = None  # Add images

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sku": "123",
                    "name": "Potato Sauce",
                    "description": "Nice tasty potato sauce",
                    "category_name": "Food",
                    "price": 1.50,
                    "quantity": 100,
                    "images": ["https://example1.com", "https://example2.com"],
                }
            ]
        }
    }


class ProductUpdate(BaseModel):
    name: str
    category_name: str
    price: float
    quantity: int
    description: Optional[str] = None
    images: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "(Updated) Potato Sauce",
                    "description": "(Updated) Nice tasty potato sauce",
                    "category_name": "Food",
                    "price": 1.50,
                    "quantity": 150,
                    "images": ["https://example1.com", "https://example2.com"],
                }
            ]
        }
    }


class ProductResponse(BaseModel):
    sku: str
    name: str
    category_name: str
    price: float
    quantity: int
    description: Optional[str] = None
    images: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sku": "123",
                    "name": "Potato Sauce",
                    "description": "Nice tasty potato sauce",
                    "category_name": "Food",
                    "price": 1.50,
                    "quantity": 100,
                    "images": ["https://example.com", "https://example.com"],
                }
            ]
        }
    }
