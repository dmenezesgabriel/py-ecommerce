from src.application.dto.customer_dto import CustomerResponse
from src.application.dto.delivery_dto import AddressResponse, DeliveryResponse
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity


def serialize_delivery(delivery: DeliveryEntity) -> DeliveryResponse:
    return DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        status=delivery.status,
        customer=CustomerResponse(
            id=delivery.customer.id,
            name=delivery.customer.name,
            email=delivery.customer.email,
            phone_number=delivery.customer.phone_number,
        ),
        address=AddressResponse(
            id=delivery.address.id,
            city=delivery.address.city,
            state=delivery.address.state,
            country=delivery.address.country,
            zip_code=delivery.address.zip_code,
        ),
    )


def serialize_customer(customer: CustomerEntity) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
    )
