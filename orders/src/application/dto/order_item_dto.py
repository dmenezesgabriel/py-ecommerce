from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_sku: str
    quantity: int

    class Config:
        json_schema_extra = {
            "examples": [{"product_sku": "123", "quantity": 2}]
        }


class OrderItemResponse(BaseModel):
    product_sku: str
    quantity: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {
                    "product_sku": "ABC123",
                    "quantity": 2,
                },
                {
                    "product_sku": "XYZ456",
                    "quantity": 1,
                },
            ]
        }
