# Py Order System

This is an ordering system system backend, with the aim of mitigating confusion among waiters and delays in preparing deliveries and orders, developed for FIAP's postgraduate software architecture course.

## Architecture

It was developed based on four microservices, Inventory, Orders, Payments and Delivery.

### Saga Pattern

To better maintain consistence of the information that pass through services it was chosen the **Choreography**-based saga pattern in which each squad has more autonomy and there is no single point of failure. Since this system composition yet present low complexity the current pattern was the best fit, but in the feature as the complexity grows we may reconsider to an Orchestrated-based one.

![diagram](docs/assets//architecture.drawio.svg)

## Run locally with Docker

```sh
make run-infra
```

```sh
make run-services
```

```sh
make show-services-logs
```

### OWASP ZAP

Reports generated on folder `zap-reports`.

### Docker HUB

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

## Run locally with Kubernetes

see `/k8s` for instructions [README](./k8s/README.md)
