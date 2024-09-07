from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_product_service
from src.application.dto.inventory_dto import InventoryUpdate
from src.application.dto.product_dto import ProductResponse
from src.application.dto.serializers import serialize_product
from src.application.services.product_service import ProductService
from src.domain.exceptions import EntityNotFound, InvalidEntity

router = APIRouter()


@router.post(
    "/inventory/{sku}/add", tags=["Inventory"], response_model=ProductResponse
)
def add_inventory(
    sku: str,
    inventory_update: InventoryUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        product = service.add_inventory(sku, inventory_update.quantity)
        return serialize_product(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/inventory/{sku}/subtract",
    tags=["Inventory"],
    response_model=ProductResponse,
)
def subtract_inventory(
    sku: str,
    inventory_update: InventoryUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        product = service.subtract_inventory(sku, inventory_update.quantity)
        return serialize_product(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidEntity as e:
        raise HTTPException(status_code=400, detail=str(e))
