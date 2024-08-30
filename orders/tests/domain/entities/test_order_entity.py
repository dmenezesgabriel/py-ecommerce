import math
from unittest.mock import MagicMock

import pytest
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.order_entity import OrderEntity, OrderStatus
from src.domain.entities.order_item_entity import OrderItemEntity
from src.domain.exceptions import InvalidEntity


def test_order_entity_initialization():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    order = OrderEntity(
        customer=customer_mock,
        order_items=[order_item_mock],
        status=OrderStatus.PENDING,
        estimated_time="2024-08-30",
        id=1,
        total_amount=100.0,
    )

    assert order.id == 1
    assert order.order_number is not None
    assert order.customer == customer_mock
    assert order.order_items == [order_item_mock]
    assert order.status == OrderStatus.PENDING
    assert math.isclose(order.total_amount, 100.0)
    assert order.estimated_time == "2024-08-30"


def test_order_entity_invalid_id():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    with pytest.raises(InvalidEntity):
        OrderEntity(
            customer=customer_mock,
            order_items=[order_item_mock],
            id=-1,
        )


def test_order_entity_invalid_order_number():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)

    order = OrderEntity(
        customer=customer_mock,
        order_items=[order_item_mock],
    )

    with pytest.raises(InvalidEntity):
        order.order_number = None

    with pytest.raises(InvalidEntity):
        order.order_number = ""


def test_order_entity_invalid_customer():
    order_item_mock = MagicMock(spec=OrderItemEntity)
    with pytest.raises(InvalidEntity):
        OrderEntity(
            customer=None,
            order_items=[order_item_mock],
        )


def test_order_entity_invalid_order_items():
    customer_mock = MagicMock(spec=CustomerEntity)
    with pytest.raises(InvalidEntity):
        OrderEntity(
            customer=customer_mock,
            order_items=[None],
        )


def test_order_entity_invalid_total_amount():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    with pytest.raises(InvalidEntity):
        OrderEntity(
            customer=customer_mock,
            order_items=[order_item_mock],
            total_amount=-100.0,
        )


def test_order_entity_invalid_estimated_time():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    with pytest.raises(InvalidEntity):
        OrderEntity(
            customer=customer_mock,
            order_items=[order_item_mock],
            estimated_time=12345,
        )


def test_add_item():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    order = OrderEntity(
        customer=customer_mock,
        order_items=[],
    )

    order.add_item(order_item_mock)

    assert order.order_items == [order_item_mock]


def test_update_status():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    order = OrderEntity(
        customer=customer_mock,
        order_items=[order_item_mock],
    )

    order.update_status(OrderStatus.SHIPPED)

    assert order.status == OrderStatus.SHIPPED


def test_to_dict():
    customer_mock = MagicMock(spec=CustomerEntity)
    customer_mock.to_dict.return_value = {"id": 1, "name": "John Doe"}

    order_item_mock = MagicMock(spec=OrderItemEntity)
    order_item_mock.to_dict.return_value = {"product_id": 1, "quantity": 2}

    order = OrderEntity(
        customer=customer_mock,
        order_items=[order_item_mock],
        id=1,
        total_amount=100.0,
        estimated_time="2024-08-30",
    )

    expected_dict = {
        "id": 1,
        "order_number": order.order_number,
        "customer": {"id": 1, "name": "John Doe"},
        "order_items": [{"product_id": 1, "quantity": 2}],
        "status": "pending",
        "total_amount": 100.0,
        "estimated_time": "2024-08-30",
    }

    assert order.to_dict() == expected_dict


def test_order_entity_setters():
    customer_mock = MagicMock(spec=CustomerEntity)
    order_item_mock = MagicMock(spec=OrderItemEntity)
    order = OrderEntity(
        customer=customer_mock,
        order_items=[order_item_mock],
    )

    order.id = 2
    assert order.id == 2

    order.order_number = "NEW_ORDER_NUMBER"
    assert order.order_number == "NEW_ORDER_NUMBER"

    new_customer_mock = MagicMock(spec=CustomerEntity)
    order.customer = new_customer_mock
    assert order.customer == new_customer_mock

    new_order_item_mock = MagicMock(spec=OrderItemEntity)
    order.order_items = [new_order_item_mock]
    assert order.order_items == [new_order_item_mock]

    order.total_amount = 200.0
    assert math.isclose(order.total_amount, 200.0)

    order.estimated_time = "2024-09-01"
    assert order.estimated_time == "2024-09-01"


@pytest.mark.parametrize("invalid_id", [-1, "string", 0])
def test_validate_id_invalid(invalid_id):
    order = OrderEntity(
        customer=MagicMock(spec=CustomerEntity),
        order_items=[MagicMock(spec=OrderItemEntity)],
    )
    with pytest.raises(InvalidEntity):
        order.id = invalid_id


def test_validate_order_number_invalid():
    order = OrderEntity(
        customer=MagicMock(spec=CustomerEntity),
        order_items=[MagicMock(spec=OrderItemEntity)],
    )
    with pytest.raises(InvalidEntity):
        order.order_number = ""


def test_validate_total_amount_invalid():
    order = OrderEntity(
        customer=MagicMock(spec=CustomerEntity),
        order_items=[MagicMock(spec=OrderItemEntity)],
    )
    with pytest.raises(InvalidEntity):
        order.total_amount = -100.0


def test_validate_estimated_time_invalid():
    order = OrderEntity(
        customer=MagicMock(spec=CustomerEntity),
        order_items=[MagicMock(spec=OrderItemEntity)],
    )
    with pytest.raises(InvalidEntity):
        order.estimated_time = 12345
