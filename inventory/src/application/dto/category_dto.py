from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Food",
                },
                {
                    "name": "Electronics",
                },
            ]
        }
    }


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Food",
                },
                {
                    "id": 2,
                    "name": "Electronics",
                },
            ]
        }
    }
