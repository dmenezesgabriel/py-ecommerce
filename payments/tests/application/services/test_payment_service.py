import time
from unittest.mock import MagicMock, patch

import pytest
from src.application.services.payment_service import PaymentService
from src.domain.entities.payment_entity import PaymentEntity, PaymentStatus
from src.domain.exceptions import (
    EntityAlreadyExists,
    EntityNotFound,
    InvalidAction,
)


# Helper function to create a mock PaymentEntity
def create_mock_payment_entity(
    payment_id="1",
    order_id=1,
    amount=100.0,
    status=PaymentStatus.PENDING.value,
):
    payment_entity = MagicMock(spec=PaymentEntity)
    payment_entity.id = payment_id
    payment_entity.order_id = order_id
    payment_entity.amount = amount
    payment_entity.status = status
    payment_entity.qr_code = (
        f"https://www.mercadopago.com.br/qr-code/{order_id}"
    )
    payment_entity.qr_code_expiration = int(time.time()) + 3600
    return payment_entity


def test_create_payment_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    # Mocking the repository find_by_order_id to return None
    payment_repository.find_by_order_id.return_value = None
    qr_code_service.create_qr_code.return_value = (
        "https://www.mercadopago.com.br/qr-code/1",
        3600,
    )

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    payment = payment_service.create_payment(
        order_id=1, amount=100.0, status=PaymentStatus.PENDING.value
    )

    payment_repository.save.assert_called_once()
    qr_code_service.create_qr_code.assert_called_once_with(1, 100.0)
    assert payment.order_id == 1
    assert payment.amount == 100.0
    assert payment.status == PaymentStatus.PENDING.value


def test_create_payment_already_exists():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    # Mocking the repository find_by_order_id to return an existing payment
    payment_repository.find_by_order_id.return_value = (
        create_mock_payment_entity()
    )

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(EntityAlreadyExists):
        payment_service.create_payment(
            order_id=1, amount=100.0, status=PaymentStatus.PENDING.value
        )


def test_get_payment_by_id_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = create_mock_payment_entity()

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    payment = payment_service.get_payment_by_id("1")

    assert payment.id == "1"
    payment_repository.find_by_id.assert_called_once_with("1")


def test_get_payment_by_id_not_found():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = None

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(EntityNotFound):
        payment_service.get_payment_by_id("1")


def test_update_payment_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = create_mock_payment_entity()

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    payment = payment_service.update_payment(
        "1", 1, 200.0, PaymentStatus.COMPLETED.value
    )

    assert payment.amount == 200.0
    assert payment.status == PaymentStatus.COMPLETED.value
    payment_repository.save.assert_called_once()


def test_update_payment_not_found():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = None

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(EntityNotFound):
        payment_service.update_payment(
            "1", 1, 200.0, PaymentStatus.COMPLETED.value
        )


def test_update_payment_canceled():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = create_mock_payment_entity(
        status=PaymentStatus.CANCELED.value
    )

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(InvalidAction):
        payment_service.update_payment(
            "1", 1, 200.0, PaymentStatus.COMPLETED.value
        )


def test_update_payment_status_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment = create_mock_payment_entity(status=PaymentStatus.PENDING.value)
    payment_repository.find_by_id.return_value = payment

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    # Manually update the status in the mock when the update_status method is called
    def update_status(new_status):
        payment.status = new_status

    payment.update_status = MagicMock(side_effect=update_status)

    updated_payment = payment_service.update_payment_status(
        "1", PaymentStatus.COMPLETED.value
    )

    assert updated_payment.status == PaymentStatus.COMPLETED.value
    payment_repository.save.assert_called_once()
    payment_publisher.publish_payment_update.assert_called_once_with(
        payment_id="1", order_id=1, status=PaymentStatus.COMPLETED.value
    )


def test_update_payment_status_invalid_action():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment = create_mock_payment_entity(status=PaymentStatus.CANCELED.value)
    payment_repository.find_by_id.return_value = payment

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(InvalidAction):
        payment_service.update_payment_status(
            "1", PaymentStatus.COMPLETED.value
        )


def test_cancel_payment_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment = create_mock_payment_entity(status=PaymentStatus.PENDING.value)
    payment_repository.find_by_id.return_value = payment

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    # Manually update the status in the mock when the update_status method is called
    def update_status(new_status):
        payment.status = new_status

    payment.update_status = MagicMock(side_effect=update_status)

    canceled_payment = payment_service.cancel_payment("1")

    assert canceled_payment.status == PaymentStatus.CANCELED.value
    payment_repository.save.assert_called_once()
    payment_publisher.publish_payment_update.assert_called_once_with(
        payment_id="1", order_id=1, status=PaymentStatus.CANCELED.value
    )


def test_cancel_payment_invalid_action():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment = create_mock_payment_entity(status=PaymentStatus.COMPLETED.value)
    payment_repository.find_by_id.return_value = payment

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(InvalidAction):
        payment_service.cancel_payment("1")


def test_delete_payment_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = create_mock_payment_entity()

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    deleted_payment = payment_service.delete_payment("1")

    payment_repository.delete.assert_called_once()
    assert deleted_payment.id == "1"


def test_delete_payment_not_found():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_repository.find_by_id.return_value = None

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(EntityNotFound):
        payment_service.delete_payment("1")


def test_handle_webhook_success():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with patch.object(
        payment_service,
        "get_payment_by_id",
        return_value=create_mock_payment_entity(),
    ) as mock_get_payment_by_id, patch.object(
        payment_service,
        "update_payment_status",
        return_value=create_mock_payment_entity(
            status=PaymentStatus.COMPLETED.value
        ),
    ) as mock_update_payment_status:

        updated_payment = payment_service.handle_webhook("1", "approved")
        assert updated_payment.status == PaymentStatus.COMPLETED.value
        mock_get_payment_by_id.assert_called_once_with("1")
        mock_update_payment_status.assert_called_once_with(
            "1", PaymentStatus.COMPLETED.value
        )


def test_handle_webhook_invalid_action():
    payment_repository = MagicMock()
    payment_publisher = MagicMock()
    qr_code_service = MagicMock()

    payment_service = PaymentService(
        payment_repository, payment_publisher, qr_code_service
    )

    with pytest.raises(InvalidAction):
        payment_service.handle_webhook("1", "unsupported_status")
