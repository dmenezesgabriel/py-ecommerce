import pytest
from pydantic import ValidationError
from src.application.dto.health_dto import HealthResponse


class TestHealthResponse:

    def test_create_health_response_valid(self):
        # Arrange & Act
        health_response = HealthResponse(
            database="healthy", rabbitmq="healthy"
        )

        # Assert
        assert health_response.database == "healthy"
        assert health_response.rabbitmq == "healthy"

    def test_create_health_response_invalid_database(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            HealthResponse(database=123, rabbitmq="healthy")  # Invalid type

    def test_create_health_response_invalid_rabbitmq(self):
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            HealthResponse(database="healthy", rabbitmq=123)  # Invalid type

    def test_health_response_to_dict(self):
        # Arrange
        health_response = HealthResponse(
            database="healthy", rabbitmq="healthy"
        )

        # Act
        health_dict = health_response.model_dump()

        # Assert
        assert health_dict == {
            "database": "healthy",
            "rabbitmq": "healthy",
        }

    def test_health_response_example(self):
        # Arrange & Act
        example = HealthResponse.model_config["json_schema_extra"]["examples"]

        # Assert
        assert example == [
            {
                "database": "healthy",
                "rabbitmq": "healthy",
            }
        ]


if __name__ == "__main__":
    pytest.main()
