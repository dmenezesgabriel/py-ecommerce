https://medium.com/@buffetbenjamin/securing-fastapi-with-keycloak-the-adventure-begins-part-1-e7eae3b79946

## Saga Pattern

```mermaid
sequenceDiagram
    participant InventoryService as Inventory Service
    participant OrderService as Order Service
    participant PaymentService as Payment Service
    participant DeliveryService as Delivery Service
    participant InventoryQueue as Inventory Queue
    participant PaymentQueue as Payment Queue
    participant DeliveryQueue as Delivery Queue

    OrderService->>InventoryService: Check inventory availability (SKU, Quantity)

    alt Inventory not available
        InventoryService-->>OrderService: Inventory not available
        OrderService-->>OrderService: Rollback order creation
    else Inventory available
        InventoryService-->>OrderService: Inventory available
        OrderService->>InventoryService: Subtract inventory (SKU, Quantity, action: subtract)
        InventoryService->>InventoryQueue: Publish inventory update message
        InventoryQueue-->>InventoryService: Confirm inventory update

        OrderService->>PaymentService: Initiate payment (Order ID, Amount, Status: Pending)
        PaymentService->>PaymentQueue: Publish payment message
        PaymentQueue-->>PaymentService: Confirm payment processing

        alt Payment successful
            PaymentService-->>OrderService: Payment confirmed (Order ID, Status: Paid)
            PaymentService->>DeliveryService: Notify delivery service (Order ID, Status: Paid)
            DeliveryService->>DeliveryQueue: Publish delivery creation message
            DeliveryQueue-->>DeliveryService: Confirm delivery creation (Status: Pending)
        else Payment failed
            PaymentService-->>OrderService: Payment failed
            OrderService-->>InventoryService: Revert inventory subtraction (SKU, Quantity)
            InventoryService->>InventoryQueue: Publish inventory revert message
            InventoryQueue-->>InventoryService: Confirm inventory revert
            OrderService-->>OrderService: Rollback order creation
        end
    end
```

## Kong ApiGateway

### Kong with FastApi

- [behind-a-proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/#providing-the-root_path)

http://localhost:8100/inventory/docs#/

### Docker

- **Check declarative config**:

```sh
docker-compose exec kong ls /usr/local/kong/declarative/
```

- **Reload Kong**:

```sh
docker-compose exec kong kong reload
```

### Urls

- **Routes**:

```sh
curl http://localhost:8101/routes
```

- **Services**:

```sh
curl http://localhost:8101/services
```

Example:

```sh
curl http://localhost:8100/inventory/health
```
