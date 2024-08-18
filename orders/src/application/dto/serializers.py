from src.application.dto.customer_dto import CustomerResponse
from src.application.dto.order_dto import OrderResponse
from src.application.dto.order_item_dto import OrderItemResponse
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity
from src.domain.entities.order_item_entity import OrderItemEntity


def serialize_order(order: OrderEntity, total_amount: float) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer=serialize_customer(order.customer),
        order_items=[serialize_order_item(item) for item in order.order_items],
        status=order.status,
        total_amount=total_amount,
    )


def serialize_order_item(order_item: OrderItemEntity) -> OrderItemResponse:
    return OrderItemResponse(
        product_sku=order_item.product_sku,
        quantity=order_item.quantity,
    )


def serialize_customer(customer: CustomerEntity) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone_number=customer.phone_number,
    )
