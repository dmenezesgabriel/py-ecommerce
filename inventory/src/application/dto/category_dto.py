from typing import Any, Dict, List

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


class CategoriesPaginatedResponse(BaseModel):
    pagination: Dict[str, Any]
    categories: List[CategoryResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "categories": [
                        {"id": 1, "name": "Food"},
                        {"id": 2, "name": "Drink"},
                        {"id": 3, "name": "Dessert"},
                    ],
                    "pagination": {
                        "current_page": 1,
                        "records_per_page": 3,
                        "number_of_pages": 3,
                        "total_records": 7,
                    },
                }
            ]
        }
    }
