from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_order_service
from src.application.dto.order_dto import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)
from src.application.dto.serializers import serialize_order
from src.application.services.order_service import OrderService
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import EntityNotFound, InvalidEntity

router = APIRouter()


@router.post("/orders/", tags=["Orders"], response_model=OrderResponse)
async def create_order(
    order: OrderCreate, service: OrderService = Depends(get_order_service)
):
    customer_entity = CustomerEntity(
        name=order.customer.name,
        email=order.customer.email,
        phone_number=order.customer.phone_number,
    )
    order_items = [
        OrderItemEntity(product_sku=item.product_sku, quantity=item.quantity)
        for item in order.order_items
    ]
    created_order = await service.create_order(customer_entity, order_items)
    return serialize_order(created_order, created_order.total_amount)


@router.get("/orders/", tags=["Orders"], response_model=List[OrderResponse])
async def read_orders(service: OrderService = Depends(get_order_service)):
    orders = await service.list_orders()
    orders_with_amounts = [
        {"order": order, "amount": await service.calculate_order_total(order)}
        for order in orders
    ]
    return [
        serialize_order(order["order"], order["amount"])
        for order in orders_with_amounts
    ]


@router.get(
    "/orders/{order_id}", tags=["Orders"], response_model=OrderResponse
)
async def read_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        order = await service.get_order_by_id(order_id)
        total_amount = await service.calculate_order_total(order)
        return serialize_order(order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/orders/by-order-number/{order_number}",
    tags=["Orders"],
    response_model=OrderResponse,
)
async def read_order_by_order_number(
    order_number: str, service: OrderService = Depends(get_order_service)
):
    try:
        order = await service.get_order_by_order_number(order_number)
        total_amount = await service.calculate_order_total(order)
        return serialize_order(order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/orders/{order_id}", tags=["Orders"], response_model=OrderResponse
)
async def update_order(
    order_id: int,
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    customer_entity = CustomerEntity(
        name=order.customer.name, email=order.customer.email
    )
    order_items = [
        OrderItemEntity(product_sku=item.product_sku, quantity=item.quantity)
        for item in order.order_items
    ]
    try:
        updated_order = await service.update_order(
            order_id, customer_entity, order_items
        )
        return serialize_order(updated_order, updated_order.total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/orders/{order_id}/status", tags=["Orders"], response_model=OrderResponse
)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
):
    try:
        updated_order = await service.update_order_status(
            order_id, status_update.status
        )
        total_amount = await service.calculate_order_total(updated_order)
        return serialize_order(updated_order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/orders/{order_id}/confirm", tags=["Orders"], response_model=OrderResponse
)
async def confirm_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        confirmed_order = await service.confirm_order(order_id)
        total_amount = await service.calculate_order_total(confirmed_order)
        return serialize_order(confirmed_order, total_amount)
    except (EntityNotFound, InvalidEntity) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/orders/{order_id}/cancel", tags=["Orders"], response_model=OrderResponse
)
async def cancel_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        canceled_order = await service.cancel_order(order_id)
        total_amount = await service.calculate_order_total(canceled_order)
        return serialize_order(canceled_order, total_amount)
    except (EntityNotFound, InvalidEntity) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/orders/{order_id}", tags=["Orders"], status_code=204)
async def delete_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        await service.delete_order(order_id)
        return {"message": "Order deleted successfully"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
