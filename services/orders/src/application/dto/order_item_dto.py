from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_sku: str
    quantity: int

    model_config = {
        "json_schema_extra": {
            "examples": [{"product_sku": "123", "quantity": 2}]
        }
    }


class OrderItemResponse(BaseModel):
    product_sku: str
    quantity: int
    name: str  # Add name field
    description: str  # Add description field
    price: float  # Add price field

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_sku": "ABC123",
                    "quantity": 2,
                    "name": "Product Name",
                    "description": "Product Description",
                    "price": 10.00,
                },
                {
                    "product_sku": "XYZ456",
                    "quantity": 1,
                    "name": "Product Name",
                    "description": "Product Description",
                    "price": 20.00,
                },
            ]
        },
    }
