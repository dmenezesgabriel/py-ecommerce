from pydantic import BaseModel


class InventoryUpdate(BaseModel):
    quantity: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "quantity": 50,
                },
                {
                    "quantity": 200,
                },
            ]
        }
    }
