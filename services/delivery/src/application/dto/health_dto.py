from pydantic import BaseModel


class HealthResponse(BaseModel):
    database: str
    rabbitmq: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "database": "healthy",
                    "rabbitmq": "healthy",
                },
            ]
        }
    }
