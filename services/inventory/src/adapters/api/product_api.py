from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_product_service
from src.application.dto.product_dto import (
    ProductCreate,
    ProductResponse,
    ProductsPaginatedResponse,
    ProductUpdate,
)
from src.application.dto.serializers import serialize_product
from src.application.services.product_service import ProductService
from src.domain.exceptions import EntityAlreadyExists, EntityNotFound

router = APIRouter()


@router.post("/products/", tags=["Product"], response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    try:
        created_product = service.create_product(
            sku=product.sku,
            name=product.name,
            category_name=product.category_name,
            price=product.price,
            quantity=product.quantity,
            description=product.description,
            images=product.images,
        )
        return serialize_product(created_product)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/products/", tags=["Product"], response_model=ProductsPaginatedResponse
)
def read_products_paginated(
    current_page: int = 1,
    records_per_page: int = 10,
    service: ProductService = Depends(get_product_service),
):
    (
        products,
        current_page,
        records_per_page,
        number_of_pages,
        total_records,
    ) = service.list_products_paginated(current_page, records_per_page)
    response = {
        "products": [serialize_product(product) for product in products],
        "pagination": {
            "current_page": current_page,
            "records_per_page": records_per_page,
            "number_of_pages": number_of_pages,
            "total_records": total_records,
        },
    }
    return response


@router.get(
    "/products/{sku}", tags=["Product"], response_model=ProductResponse
)
def read_product(
    sku: str, service: ProductService = Depends(get_product_service)
):
    try:
        product = service.get_product_by_sku(sku)
        return serialize_product(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/products/{sku}", tags=["Product"], response_model=ProductResponse
)
def update_product(
    sku: str,
    product: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        updated_product = service.update_product(
            sku=sku,
            name=product.name,
            category_name=product.category_name,
            price=product.price,
            quantity=product.quantity,
            description=product.description,
            images=product.images,
        )
        return serialize_product(updated_product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/products/{sku}", tags=["Product"], response_model=ProductResponse
)
def delete_product(
    sku: str, service: ProductService = Depends(get_product_service)
):
    try:
        deleted_product = service.delete_product(sku)
        return serialize_product(deleted_product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/products/by-category/{category_name}",
    tags=["Product"],
    response_model=List[ProductResponse],
)
def get_products_by_category(
    category_name: str, service: ProductService = Depends(get_product_service)
):
    try:
        products = service.get_products_by_category(category_name)
        return [serialize_product(product) for product in products]
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
