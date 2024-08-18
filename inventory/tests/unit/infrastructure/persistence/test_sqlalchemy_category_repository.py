from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.sql import operators
from src.domain.entities.category_entity import CategoryEntity
from src.infrastructure.persistence.models import CategoryModel
from src.infrastructure.persistence.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)


class TestSQLAlchemyCategoryRepository:

    def test_save_category(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyCategoryRepository(mock_session)
        category = CategoryEntity(name="Electronics")
        mock_category_model_instance = MagicMock()
        mock_category_model_instance.id = 1
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        with patch(
            "src.infrastructure.persistence.sqlalchemy_category_repository.CategoryModel",
            return_value=mock_category_model_instance,
        ):
            # Act
            repository.save(category)

            # Assert
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(
                mock_category_model_instance
            )
            assert category.id == 1

    def test_find_by_name_found(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyCategoryRepository(mock_session)
        mock_category_model_instance = MagicMock()
        mock_category_model_instance.name = "Electronics"
        mock_category_model_instance.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_category_model_instance
        )

        # Act
        result = repository.find_by_name("Electronics")

        # Assert
        mock_session.query.assert_called_once_with(CategoryModel)
        args, _ = mock_session.query.return_value.filter.call_args
        assert args[0].left.name == "name"
        assert args[0].right.value == "Electronics"
        assert args[0].operator == operators.eq
        mock_session.query.return_value.filter.return_value.first.assert_called_once()
        assert result is not None
        assert result.id == 1
        assert result.name == "Electronics"

    def test_find_by_name_not_found(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyCategoryRepository(mock_session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        # Act
        result = repository.find_by_name("NonExisting")

        # Assert
        mock_session.query.assert_called_once_with(CategoryModel)
        args, _ = mock_session.query.return_value.filter.call_args
        assert args[0].left.name == "name"
        assert args[0].right.value == "NonExisting"
        assert args[0].operator == operators.eq
        mock_session.query.return_value.filter.return_value.first.assert_called_once()
        assert result is None

    def test_list_all_categories(self):
        # Arrange
        mock_session = MagicMock()
        repository = SQLAlchemyCategoryRepository(mock_session)
        mock_category_model_instance = MagicMock()
        mock_category_model_instance.id = 1
        mock_category_model_instance.name = "Electronics"
        mock_session.query.return_value.all.return_value = [
            mock_category_model_instance
        ]

        # Act
        result = repository.list_all()

        # Assert
        mock_session.query.assert_called_once_with(CategoryModel)
        mock_session.query.return_value.all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Electronics"


if __name__ == "__main__":
    pytest.main()
