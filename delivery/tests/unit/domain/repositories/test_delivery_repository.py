import unittest

from src.domain.repositories.delivery_repository import DeliveryRepository


# A concrete subclass that does not implement the abstract methods
class ConcreteDeliveryRepository(DeliveryRepository):
    pass


class TestDeliveryRepository(unittest.TestCase):

    def test_has_save_method(self):
        # Act & Assert
        self.assertTrue(hasattr(DeliveryRepository, "save"))
        self.assertTrue(callable(getattr(DeliveryRepository, "save", None)))

    def test_has_find_by_id_method(self):
        # Act & Assert
        self.assertTrue(hasattr(DeliveryRepository, "find_by_id"))
        self.assertTrue(
            callable(getattr(DeliveryRepository, "find_by_id", None))
        )

    def test_has_find_by_order_id_method(self):
        # Act & Assert
        self.assertTrue(hasattr(DeliveryRepository, "find_by_order_id"))
        self.assertTrue(
            callable(getattr(DeliveryRepository, "find_by_order_id", None))
        )

    def test_has_delete_method(self):
        # Act & Assert
        self.assertTrue(hasattr(DeliveryRepository, "delete"))
        self.assertTrue(callable(getattr(DeliveryRepository, "delete", None)))

    def test_has_list_all_method(self):
        # Act & Assert
        self.assertTrue(hasattr(DeliveryRepository, "list_all"))
        self.assertTrue(
            callable(getattr(DeliveryRepository, "list_all", None))
        )


if __name__ == "__main__":
    unittest.main()
