from typing import Dict, List, Optional

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    current_page: int
    records_per_page: int
    number_of_pages: int
    total_records: int


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


class ProductsPaginatedResponse(BaseModel):
    products: List[ProductResponse]
    pagination: PaginationMeta

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "products": [
                        {
                            "sku": "123ABC",
                            "name": "Laptop",
                            "category_name": "Electronics",
                            "price": 999.99,
                            "quantity": 50,
                            "description": "High-end gaming laptop",
                            "images": ["https://example.com/image1.jpg"],
                        },
                        {
                            "sku": "456DEF",
                            "name": "Smartphone",
                            "category_name": "Electronics",
                            "price": 699.99,
                            "quantity": 200,
                            "description": "Latest model smartphone",
                            "images": ["https://example.com/image2.jpg"],
                        },
                    ],
                    "pagination": {
                        "current_page": 1,
                        "records_per_page": 2,
                        "number_of_pages": 5,
                        "total_records": 10,
                    },
                }
            ]
        }
    }
