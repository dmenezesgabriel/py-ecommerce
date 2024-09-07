from typing import List

from fastapi import APIRouter, Depends, HTTPException
from src.adapters.dependencies import get_payment_service
from src.application.dto.payment_dto import (
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
    WebhookPayload,
)
from src.application.dto.serializers import serialize_payment
from src.application.services.payment_service import PaymentService
from src.domain.entities.payment_entity import PaymentEntity
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidAction,
)

router = APIRouter()


@router.post("/payments/", tags=["Payments"], response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        created_payment = service.create_payment(
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        return serialize_payment(created_payment)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/payments/", tags=["Payments"], response_model=List[PaymentResponse]
)
def read_payments(service: PaymentService = Depends(get_payment_service)):
    payments = service.payment_repository.db.find()
    return [
        serialize_payment(
            PaymentEntity(
                id=str(payment["_id"]),
                order_id=payment["order_id"],
                amount=payment["amount"],
                status=payment["status"],
                qr_code=payment.get("qr_code"),
                qr_code_expiration=payment.get("qr_code_expiration"),
            )
        )
        for payment in payments
    ]


@router.get(
    "/payments/{payment_id}", tags=["Payments"], response_model=PaymentResponse
)
def read_payment(
    payment_id: str, service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = service.get_payment_by_id(payment_id)
        return serialize_payment(payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/payments/by-order-id/{order_id}",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def read_payment_by_order_id(
    order_id: int, service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = service.get_payment_by_order_id(order_id)
        return serialize_payment(payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/payments/{payment_id}", tags=["Payments"], response_model=PaymentResponse
)
def update_payment(
    payment_id: str,
    payment: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment(
            payment_id=payment_id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/payments/webhook",
    tags=["Payments"],
    response_model=PaymentResponse,
)
async def handle_webhook(
    payload: WebhookPayload,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        payment_id = payload.payment_id
        status = payload.status

        updated_payment = service.handle_webhook(payment_id, status)
        return serialize_payment(updated_payment)

    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/payments/{payment_id}", tags=["Payments"])
def delete_payment(
    payment_id: str, service: PaymentService = Depends(get_payment_service)
):
    try:
        service.delete_payment(payment_id)
        return {"detail": "Payment deleted"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
