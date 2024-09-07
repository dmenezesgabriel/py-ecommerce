from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_order_service
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse
from src.application.dto.serializers import serialize_customer
from src.application.services.order_service import OrderService
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.exceptions import EntityAlreadyExists, EntityNotFound

router = APIRouter()


@router.get(
    "/customers/", tags=["Customer"], response_model=List[CustomerResponse]
)
async def read_customers(service: OrderService = Depends(get_order_service)):
    customers = service.get_all_customers()
    return [serialize_customer(customer) for customer in customers]


@router.get(
    "/customers/{email}", tags=["Customer"], response_model=CustomerResponse
)
async def read_customer(
    email: str, service: OrderService = Depends(get_order_service)
):
    customer = service.get_customer_by_email(email)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return serialize_customer(customer)


@router.post("/customers/", tags=["Customer"], response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    service: OrderService = Depends(get_order_service),
):
    customer_entity = CustomerEntity(
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
    )
    try:
        created_customer = service.create_customer(customer_entity)
        return serialize_customer(created_customer)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/customers/{email}",
    tags=["Customer"],
    response_model=CustomerResponse,
)
async def update_customer(
    email: str,
    customer: CustomerCreate,
    service: OrderService = Depends(get_order_service),
):
    updated_customer_entity = CustomerEntity(
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
    )
    try:
        updated_customer = service.update_customer(
            email, updated_customer_entity
        )
        return serialize_customer(updated_customer)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/customers/", tags=["Customer"], status_code=204)
async def delete_customer(
    email: str, service: OrderService = Depends(get_order_service)
):
    try:
        service.delete_customer(email)
        return {"message": "Customer deleted successfully"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
