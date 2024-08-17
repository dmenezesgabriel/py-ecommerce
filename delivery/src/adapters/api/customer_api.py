from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_delivery_service
from src.application.dto.customer_dto import CustomerCreate, CustomerResponse
from src.application.dto.serializers import serialize_customer
from src.application.services.delivery_service import DeliveryService
from src.domain.entities.customer_entity import CustomerEntity

router = APIRouter()


@router.get(
    "/customers/", tags=["Customer"], response_model=List[CustomerResponse]
)
async def read_customers(
    service: DeliveryService = Depends(get_delivery_service),
):
    customers = service.list_customers()
    return [serialize_customer(customer) for customer in customers]


@router.get(
    "/customers/{email}", tags=["Customer"], response_model=CustomerResponse
)
async def read_customer(
    email: str, service: DeliveryService = Depends(get_delivery_service)
):
    customer = service.get_customer_by_email(email)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return serialize_customer(customer)


@router.post("/customers/", tags=["Customer"], response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    service: DeliveryService = Depends(get_delivery_service),
):
    customer_entity = CustomerEntity(
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
    )
    service.save_customer(customer_entity)
    return serialize_customer(customer_entity)


@router.put(
    "/customers/{email}",
    tags=["Customer"],
    response_model=CustomerResponse,
)
async def update_customer(
    email: str,
    customer: CustomerCreate,
    service: DeliveryService = Depends(get_delivery_service),
):
    customer_entity = service.get_customer_by_email(email)
    if not customer_entity:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_entity.name = customer.name
    customer_entity.email = customer.email
    customer_entity.phone_number = customer.phone_number
    service.save_customer(customer_entity)
    return serialize_customer(customer_entity)


@router.delete("/customers/", tags=["Customer"], status_code=204)
async def delete_customer(
    email: str, service: DeliveryService = Depends(get_delivery_service)
):
    customer_entity = service.get_customer_by_email(email)
    if not customer_entity:
        raise HTTPException(status_code=404, detail="Customer not found")
    service.delete_customer(customer_entity)
    return {"message": "Customer deleted successfully"}
