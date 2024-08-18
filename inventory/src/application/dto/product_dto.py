from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    category_name: str
    price: float
    quantity: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sku": "123",
                    "name": "Potato Sauce",
                    "category_name": "Food",
                    "price": 1.50,
                    "quantity": 100,
                }
            ]
        }
    }


class ProductUpdate(BaseModel):
    name: str
    category_name: str
    price: float
    quantity: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Potato Sauce",
                    "category_name": "Food",
                    "price": 1.50,
                    "quantity": 150,
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sku": "123",
                    "name": "Potato Sauce",
                    "category_name": "Food",
                    "price": 1.50,
                    "quantity": 100,
                }
            ]
        }
    }
