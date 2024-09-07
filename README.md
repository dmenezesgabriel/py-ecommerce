# Py Order System

This is an Order system microservice based application written in Python. It can be used as a backend for an ecommerce app, a fastfood tablet or totem order system or anything similar.

The system is composed by four applications: Inventory, Orders, Payments and Delivery and use a **Cerography-based** saga pattern to assure consistency between services. This pattern was chosen due to the current level of complexity of this system, autonomy of each system and to avoid having a single point of failure that can make the hole system inoperative.

First we need to register products in the inventory, once we have our products there, the customer can create an order. This order must be confirmed if not will be pending and it can be canceled also if desired.

When an Order in this system is confirmed, it will generate a pending payment, with a **mocked** external payment provider integration and a fake QR code. The payment service has a webhook route to set the payment status to approved or denied. And then the Order in order _service_ should be also updated.

There is a fourth service called Delivery, where a delivery can be created for an order with an specific address and customer, once the delivery is updated this will also change the order stratus in orders _service_.

Since both orders _service_ and delivery _service_ have customer information, we offer a data protection compliant route to permanently anonimize all the customer info in each of the services.

## Run locally

```sh
make run-infra
```

```sh
make run-services
```

```sh
make show-services-logs
```

# Docker

- **Login**:

```sh
docker login registry-1.docker.io
```

- **Build all services**:

```sh
make buildall
```

- **Push all services**:

```sh
make pushall
```
