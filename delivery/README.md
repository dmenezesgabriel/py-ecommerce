# Delivery Service

## Ports and Adapters

```sh
delivery_service/
│
├── domain/
│   ├── entities/
│   │   ├── delivery_entity.py
│   │   ├── customer_entity.py
│   │   └── address_entity.py
│   ├── exceptions/
│   │   └── exceptions.py
│   └── repositories/
│       ├── delivery_repository.py
│       └── customer_repository.py
│
├── application/
│   ├── services/
│   │   ├── delivery_service.py
│   │   └── order_verification_service.py
│   └── dto/
│       ├── delivery_dto.py
│       └── customer_dto.py
│
├── infrastructure/
│   ├── persistence/
│   │   ├── sqlalchemy_delivery_repository.py
│   │   ├── sqlalchemy_customer_repository.py
│   │   ├── models.py
│   │   └── db_setup.py
│   ├── messaging/
│   │   ├── delivery_publisher.py
│   ├── health/
│   │   └── health_service.py
│   └── config/
│       └── config.py
│
├── adapters/
│   ├── api/
│   │   ├── delivery_api.py
│   │   ├── customer_api.py
│   │   └── health_api.py
│   └── messaging/
│       └── rabbitmq_adapter.py
│
├── main.py
└── requirements.txt
```
