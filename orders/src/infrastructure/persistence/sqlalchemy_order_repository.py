from typing import List, Optional

from sqlalchemy.orm import Session
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.repositories.order_repository import OrderRepository
from src.infrastructure.persistence.models import (
    CustomerModel,
    OrderItemModel,
    OrderModel,
)


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, order: OrderEntity):
        customer_model = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == order.customer.email)
            .first()
        )
        if not customer_model:
            customer_model = CustomerModel(
                name=order.customer.name,
                email=order.customer.email,
                phone_number=order.customer.phone_number,
            )
            self.db.add(customer_model)
            self.db.commit()
            self.db.refresh(customer_model)

        if order.id:
            db_order = (
                self.db.query(OrderModel)
                .filter(OrderModel.id == order.id)
                .first()
            )
            db_order.estimated_time = order.estimated_time
            db_order.status = order.status
        else:
            db_order = OrderModel(
                order_number=order.order_number,
                customer_id=customer_model.id,
                status=order.status,
                estimated_time=order.estimated_time,
            )
            self.db.add(db_order)
            self.db.commit()
            self.db.refresh(db_order)

        self.db.query(OrderItemModel).filter(
            OrderItemModel.order_id == db_order.id
        ).delete()

        for item in order.order_items:
            db_order_item = OrderItemModel(
                order_id=db_order.id,
                product_sku=item.product_sku,
                quantity=item.quantity,
            )
            self.db.add(db_order_item)

        self.db.commit()
        self.db.refresh(db_order)
        order.id = db_order.id
        order.customer.id = customer_model.id

    def find_by_id(self, order_id: int) -> Optional[OrderEntity]:
        db_order = (
            self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        )
        if db_order:
            customer = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.id == db_order.customer_id)
                .first()
            )
            order_items = (
                self.db.query(OrderItemModel)
                .filter(OrderItemModel.order_id == db_order.id)
                .all()
            )
            return OrderEntity(
                id=db_order.id,
                customer=CustomerEntity(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                    phone_number=customer.phone_number,
                ),
                order_items=[
                    OrderItemEntity(
                        id=item.id,
                        product_sku=item.product_sku,
                        quantity=item.quantity,
                    )
                    for item in order_items
                ],
                status=db_order.status,
                order_number=db_order.order_number,
                estimated_time=db_order.estimated_time,
            )
        return None

    def find_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        db_order = (
            self.db.query(OrderModel)
            .filter(OrderModel.order_number == order_number)
            .first()
        )
        if db_order:
            customer = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.id == db_order.customer_id)
                .first()
            )
            order_items = (
                self.db.query(OrderItemModel)
                .filter(OrderItemModel.order_id == db_order.id)
                .all()
            )
            return OrderEntity(
                id=db_order.id,
                customer=CustomerEntity(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                    phone_number=customer.phone_number,
                ),
                order_items=[
                    OrderItemEntity(
                        id=item.id,
                        product_sku=item.product_sku,
                        quantity=item.quantity,
                    )
                    for item in order_items
                ],
                status=db_order.status,
                order_number=db_order.order_number,
                estimated_time=db_order.estimated_time,
            )
        return None

    def delete(self, order: OrderEntity):
        db_order = (
            self.db.query(OrderModel).filter(OrderModel.id == order.id).first()
        )
        if db_order:
            self.db.delete(db_order)
            self.db.commit()

    def list_all(self) -> List[OrderEntity]:
        db_orders = self.db.query(OrderModel).all()
        return [
            OrderEntity(
                id=db_order.id,
                customer=CustomerEntity(
                    id=db_order.customer.id,
                    name=db_order.customer.name,
                    email=db_order.customer.email,
                    phone_number=db_order.customer.phone_number,
                ),
                order_items=[
                    OrderItemEntity(
                        id=item.id,
                        product_sku=item.product_sku,
                        quantity=item.quantity,
                    )
                    for item in db_order.order_items
                ],
                status=db_order.status,
                order_number=db_order.order_number,
                estimated_time=db_order.estimated_time,
            )
            for db_order in db_orders
        ]
