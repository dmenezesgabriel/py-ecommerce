import unittest
from unittest.mock import MagicMock, patch


class TestDBSetup(unittest.TestCase):

    @patch("src.infrastructure.persistence.db_setup.SessionLocal")
    def test_get_db(self, mock_SessionLocal):
        # Arrange
        mock_db_instance = MagicMock()
        mock_SessionLocal.return_value = mock_db_instance

        # Act
        from src.infrastructure.persistence.db_setup import get_db

        gen = get_db()
        db = next(gen)

        # Assert
        mock_SessionLocal.assert_called_once()
        self.assertEqual(db, mock_db_instance)

        # Act
        with self.assertRaises(StopIteration):
            next(gen)

        # Assert that the session was closed
        mock_db_instance.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
