# Orders Service

## Ports and Adapters

```sh
order_service/
│
├── domain/
│   ├── entities/
│   │   ├── order_entity.py
│   │   ├── customer_entity.py
│   │   ├── order_item_entity.py
│   │   └── exceptions.py
│   └── repositories/
│       ├── order_repository.py
│       └── customer_repository.py
│
├── application/
│   ├── dto/
│   │   ├── order_dto.py
│   │   ├── customer_dto.py
│   │   └── order_item_dto.py
│   └── services/
│       └── order_service.py
│
├── infrastructure/
│   ├── persistence/
│   │   ├── sqlalchemy_order_repository.py
│   │   ├── sqlalchemy_customer_repository.py
│   │   ├── models.py
│   │   └── db_setup.py
│   ├── messaging/
│   │   ├── payment_subscriber.py
│   │   ├── delivery_subscriber.py
│   │   ├── inventory_publisher.py
│   │   └── order_update_publisher.py
│   ├── health/
│   │   └── health_service.py
│   └── config/
│       └── config.py
│
├── adapters/
│   ├── api/
│   │   ├── order_api.py
│   │   ├── customer_api.py
│   │   └── health_api.py
│   └── messaging/
│       ├── payment_subscriber.py
│       └── delivery_subscriber.py
│
├── main.py
└── requirements.txt

```
