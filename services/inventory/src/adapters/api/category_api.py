from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_product_service
from src.application.dto.category_dto import (
    CategoriesPaginatedResponse,
    CategoryCreate,
    CategoryResponse,
)
from src.application.dto.serializers import serialize_category
from src.application.services.product_service import ProductService
from src.domain.exceptions import EntityAlreadyExists

router = APIRouter()


@router.post(
    "/categories/", tags=["Categories"], response_model=CategoryResponse
)
def create_category(
    category: CategoryCreate,
    service: ProductService = Depends(get_product_service),
):
    try:
        created_category = service.create_category(name=category.name)
        return serialize_category(created_category)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/categories/",
    tags=["Categories"],
    response_model=CategoriesPaginatedResponse,
)
def list_categories_paginated(
    current_page: int = 1,
    records_per_page: int = 3,  # Example default value
    service: ProductService = Depends(get_product_service),
):
    (
        categories,
        current_page,
        records_per_page,
        number_of_pages,
        total_records,
    ) = service.list_categories_paginated(current_page, records_per_page)

    response = {
        "categories": [
            serialize_category(category) for category in categories
        ],
        "pagination": {
            "current_page": current_page,
            "records_per_page": records_per_page,
            "number_of_pages": number_of_pages,
            "total_records": total_records,
        },
    }
    return response
