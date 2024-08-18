from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_product_service
from src.application.dto.category_dto import CategoryCreate, CategoryResponse
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
    "/categories/", tags=["Categories"], response_model=List[CategoryResponse]
)
def list_categories(service: ProductService = Depends(get_product_service)):
    categories = service.list_categories()
    return [serialize_category(category) for category in categories]
