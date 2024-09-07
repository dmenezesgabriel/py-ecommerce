import unittest

from src.domain.repositories.customer_repository import CustomerRepository


class TestCustomerRepository(unittest.TestCase):

    def test_has_save_method(self):
        # Act & Assert
        self.assertTrue(hasattr(CustomerRepository, "save"))
        self.assertTrue(callable(getattr(CustomerRepository, "save", None)))

    def test_has_find_by_email_method(self):
        # Act & Assert
        self.assertTrue(hasattr(CustomerRepository, "find_by_email"))
        self.assertTrue(
            callable(getattr(CustomerRepository, "find_by_email", None))
        )

    def test_has_list_all_method(self):
        # Act & Assert
        self.assertTrue(hasattr(CustomerRepository, "list_all"))
        self.assertTrue(
            callable(getattr(CustomerRepository, "list_all", None))
        )

    def test_has_delete_method(self):
        # Act & Assert
        self.assertTrue(hasattr(CustomerRepository, "delete"))
        self.assertTrue(callable(getattr(CustomerRepository, "delete", None)))


if __name__ == "__main__":
    unittest.main()
