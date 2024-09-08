# Py Order System

This is an micro service based order system that counts with three services:

- Inventory
- Orders
- Payments
- Delivery

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

## Run locally with Kubernetes

see `/k8s` for instructions [README](./k8s/README.md)
