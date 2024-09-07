## Payments Service

## Ports and Adapters

```sh
payments_service/
│
├── domain/
│   ├── entities/
│   │   ├── payment_entity.py
│   ├── exceptions/
│   │   └── exceptions.py
│   └── repositories/
│       └── payment_repository.py
│
├── application/
│   ├── services/
│   │   ├── payment_service.py
│   │   ├── qr_code_service.py
│   │   └── health_service.py
│   └── dto/
│       ├── payment_dto.py
│       └── webhook_dto.py
│
├── infrastructure/
│   ├── persistence/
│   │   ├── mongodb_payment_repository.py
│   │   └── db_setup.py
│   ├── messaging/
│   │   ├── payment_publisher.py
│   │   ├── order_subscriber.py
│   │   └── rabbitmq_adapter.py
│   ├── health/
│   │   └── health_service.py
│   └── config/
│       └── config.py
│
├── adapters/
│   ├── api/
│   │   ├── payment_api.py
│   │   ├── webhook_api.py
│   │   └── health_api.py
│   └── messaging/
│       └── rabbitmq_adapter.py
│
├── main.py
└── requirements.txt
```
