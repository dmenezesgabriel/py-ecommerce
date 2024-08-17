from pydantic import BaseModel


class HealthResponse(BaseModel):
    database: str
    rabbitmq: str

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "database": "healthy",
                    "rabbitmq": "healthy",
                },
            ]
        }
