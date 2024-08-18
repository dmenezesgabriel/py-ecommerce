## Inventory Service

## Ports and Adapters

```sh
inventory_service/
│
├── domain/
│   ├── entities/
│   │   ├── product_entity.py
│   │   ├── category_entity.py
│   │   ├── price_entity.py
│   │   └── inventory_entity.py
│   ├── exceptions/
│   │   └── exceptions.py
│   └── repositories/
│       ├── product_repository.py
│       └── category_repository.py
│
├── application/
│   ├── services/
│   │   ├── product_service.py
│   │   └── health_service.py
│   └── dto/
│       ├── product_dto.py
│       ├── category_dto.py
│       └── inventory_dto.py
│
├── infrastructure/
│   ├── persistence/
│   │   ├── sqlalchemy_product_repository.py
│   │   ├── sqlalchemy_category_repository.py
│   │   ├── models.py
│   │   └── db_setup.py
│   ├── messaging/
│   │   ├── inventory_subscriber.py
│   │   └── rabbitmq_adapter.py
│   ├── health/
│   │   └── health_service.py
│   └── config/
│       └── config.py
│
├── adapters/
│   ├── api/
│   │   ├── product_api.py
│   │   ├── category_api.py
│   │   └── health_api.py
│   └── messaging/
│       └── rabbitmq_adapter.py
│
├── main.py
└── requirements.txt
```
