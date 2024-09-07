from unittest.mock import MagicMock, patch

from src.adapters.dependencies import get_health_service, get_product_service


class TestDependencies:

    @patch("src.adapters.dependencies.get_db")
    @patch("src.adapters.dependencies.HealthService")
    @patch("src.config.Config.BROKER_HOST", "rabbitmq")
    def test_get_health_service(self, mock_health_service, mock_get_db):
        # Arrange
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session
        mock_health_service_instance = MagicMock()
        mock_health_service.return_value = mock_health_service_instance

        # Act
        result = get_health_service(db=mock_db_session)

        # Assert
        mock_get_db.assert_not_called()
        mock_health_service.assert_called_once_with(
            mock_db_session, rabbitmq_host="rabbitmq"
        )
        assert result == mock_health_service_instance

    @patch("src.adapters.dependencies.get_db")
    @patch("src.adapters.dependencies.SQLAlchemyProductRepository")
    @patch("src.adapters.dependencies.SQLAlchemyCategoryRepository")
    @patch("src.adapters.dependencies.ProductService")
    def test_get_product_service(
        self,
        mock_product_service,
        mock_sqlalchemy_category_repository,
        mock_sqlalchemy_product_repository,
        mock_get_db,
    ):
        # Arrange
        mock_db_session = MagicMock()
        mock_get_db.return_value = mock_db_session

        mock_product_repository = MagicMock()
        mock_category_repository = MagicMock()
        mock_sqlalchemy_product_repository.return_value = (
            mock_product_repository
        )
        mock_sqlalchemy_category_repository.return_value = (
            mock_category_repository
        )

        mock_product_service_instance = MagicMock()
        mock_product_service.return_value = mock_product_service_instance

        # Act
        result = get_product_service(db=mock_db_session)

        # Assert
        mock_get_db.assert_not_called()
        mock_sqlalchemy_product_repository.assert_called_once_with(
            mock_db_session
        )
        mock_sqlalchemy_category_repository.assert_called_once_with(
            mock_db_session
        )
        mock_product_service.assert_called_once_with(
            mock_product_repository, mock_category_repository
        )
        assert result == mock_product_service_instance
