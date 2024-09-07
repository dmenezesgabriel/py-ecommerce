from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_delivery_service
from src.application.dto.delivery_dto import (
    DeliveryCreate,
    DeliveryResponse,
    DeliveryStatus,
    DeliveryStatusUpdate,
)
from src.application.dto.serializers import serialize_delivery
from src.application.services.delivery_service import DeliveryService
from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.exceptions import EntityNotFound, InvalidOperation

router = APIRouter()


@router.post(
    "/deliveries/", tags=["delivery"], response_model=DeliveryResponse
)
async def create_delivery(
    delivery: DeliveryCreate,
    service: DeliveryService = Depends(get_delivery_service),
):
    customer_entity = CustomerEntity(
        name=delivery.customer.name,
        email=delivery.customer.email,
        phone_number=delivery.customer.phone_number,
    )
    address_entity = AddressEntity(
        city=delivery.address.city,
        state=delivery.address.state,
        country=delivery.address.country,
        zip_code=delivery.address.zip_code,
    )
    try:
        created_delivery = await service.create_delivery(
            order_id=delivery.order_id,
            delivery_address=delivery.delivery_address,
            delivery_date=delivery.delivery_date,
            status=delivery.status,
            customer=customer_entity,
            address=address_entity,
        )
        return serialize_delivery(created_delivery)
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/deliveries/", tags=["delivery"], response_model=List[DeliveryResponse]
)
async def read_deliveries(
    service: DeliveryService = Depends(get_delivery_service),
):
    deliveries = service.list_deliveries()
    return [serialize_delivery(delivery) for delivery in deliveries]


@router.get(
    "/deliveries/{delivery_id}",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def read_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        delivery = service.get_delivery_by_id(delivery_id)
        return serialize_delivery(delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/deliveries/by-order-id/{order_id}",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def read_delivery_by_order_id(
    order_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        delivery = await service.get_delivery_by_order_id(order_id)
        return serialize_delivery(delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/deliveries/{delivery_id}",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def update_delivery(
    delivery_id: int,
    delivery: DeliveryCreate,
    service: DeliveryService = Depends(get_delivery_service),
):
    customer_entity = CustomerEntity(
        name=delivery.customer.name,
        email=delivery.customer.email,
        phone_number=delivery.customer.phone_number,
    )
    address_entity = AddressEntity(
        city=delivery.address.city,
        state=delivery.address.state,
        country=delivery.address.country,
        zip_code=delivery.address.zip_code,
    )
    try:
        updated_delivery = await service.update_delivery(
            delivery_id=delivery_id,
            order_id=delivery.order_id,
            delivery_address=delivery.delivery_address,
            delivery_date=delivery.delivery_date,
            status=delivery.status,
            customer=customer_entity,
            address=address_entity,
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/deliveries/{delivery_id}/status",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    service: DeliveryService = Depends(get_delivery_service),
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, status_update.status
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/deliveries/{delivery_id}/delivered",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def set_delivery_delivered(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, DeliveryStatus.DELIVERED
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/deliveries/{delivery_id}/in-transit",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def set_delivery_in_transit(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, DeliveryStatus.IN_TRANSIT
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/deliveries/{delivery_id}/cancel",
    tags=["delivery"],
    response_model=DeliveryResponse,
)
async def cancel_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, DeliveryStatus.CANCELED
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/deliveries/{delivery_id}",
    tags=["delivery"],
)
async def delete_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        await service.delete_delivery(delivery_id)
        return {"message": "Delivery deleted successfully"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))
