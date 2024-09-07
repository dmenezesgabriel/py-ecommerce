# K8s

## Usage

- **Start Minikube**:

```sh
minikube delete
minikube start
```

- **Get all pods**:

```sh
kubectl --context=minikube get po -A
```

### Namespace

- **Apply**:

```sh
kubectl --context=minikube apply -f namespace.yaml
```

- **Get**:

```sh
kubectl --context=minikube get namespaces
```

- **Delete**:

```sh
# kubectl --context=minikube delete -f namespace.yaml
```

### Postgres

- **Apply**:

```sh
kubectl --context=minikube apply -f postgres/secret.yaml -n ecommerce
kubectl --context=minikube apply -f postgres/pv.yaml -n ecommerce
kubectl --context=minikube apply -f postgres/pvc.yaml -n ecommerce
kubectl --context=minikube apply -f postgres/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f postgres/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f postgres/node-port.yaml -n ecommerce
kubectl port-forward service/postgres-nodeport-srv --address 0.0.0.0 30432:5432 -n ecommerce
```

It should be accessible at localhost:30432

#### Create databases

- **Apply**:

```sh
kubectl --context=minikube kustomize postgres -n ecommerce
kubectl --context=minikube apply -k postgres -n ecommerce
kubectl logs job/run-postgres-init-scripts -n ecommerce
```

```sh
# kubectl --context=minikube delete -k postgres -n ecommerce
```

#### Services database migrations

```sh
kubectl --context=minikube apply -f shared/secrets/database-secrets.yaml -n ecommerce
```

#### Inventory

- **Apply Migrations**:

```sh
kubectl --context=minikube apply -f jobs/inventory-migration-job.yaml -n ecommerce

kubectl --context=minikube logs job/inventory-migration-job -n ecommerce
```

```sh
# kubectl --context=minikube delete -f jobs/inventory-migration-job.yaml -n ecommerce
```

#### Orders

- **Apply Migrations**:

```sh
kubectl --context=minikube apply -f jobs/orders-migration-job.yaml -n ecommerce

kubectl --context=minikube logs job/orders-migration-job -n ecommerce
```

```sh
# kubectl --context=minikube delete -f jobs/orders-migration-job.yaml -n ecommerce
```

#### Delivery

- **Apply Migrations**:

```sh
kubectl --context=minikube apply -f jobs/delivery-migration-job.yaml -n ecommerce

kubectl --context=minikube logs job/delivery-migration-job -n ecommerce
```

```sh
# kubectl --context=minikube delete -f jobs/delivery-migration-job.yaml -n ecommerce
```

### Mongo

- **Apply**:

```sh
# If secrets not already applied:
# kubectl --context=minikube apply -f shared/secrets/database-secrets.yaml -n ecommerce

kubectl --context=minikube apply -f mongo/pv.yaml -n ecommerce
kubectl --context=minikube apply -f mongo/pvc.yaml -n ecommerce
kubectl --context=minikube apply -f mongo/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f mongo/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f mongo/node-port.yaml -n ecommerce
kubectl port-forward service/mongo-nodeport-srv --address 0.0.0.0 30433:27017 -n ecommerce
```

It should be accessible at localhost:30433

### RabbitMq

- **Apply**:

```sh
kubectl --context=minikube apply -f rabbitmq/rabbitmq-config.yaml -n ecommerce
kubectl --context=minikube apply -f rabbitmq/rabbitmq-definitions.yaml -n ecommerce
kubectl --context=minikube apply -f rabbitmq/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f rabbitmq/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f rabbitmq/node-port.yaml -n ecommerce
kubectl port-forward service/rabbitmq-nodeport-srv --address 0.0.0.0 30434:15672 -n ecommerce
```

It should be accessible at localhost:30434

### Services

#### Inventory

- **Apply**:

```sh
kubectl --context=minikube apply -f inventory/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f inventory/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f inventory/node-port.yaml -n ecommerce
kubectl port-forward service/inventory-nodeport-srv --address 0.0.0.0 30001:8001 -n ecommerce
```

It should be accessible at localhost:30001/docs

#### Orders

- **Apply**:

```sh
kubectl --context=minikube apply -f orders/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f orders/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f orders/node-port.yaml -n ecommerce
kubectl port-forward service/orders-nodeport-srv --address 0.0.0.0 30002:8002 -n ecommerce
```

It should be accessible at localhost:30002/docs

#### Payments

- **Apply**:

```sh
kubectl --context=minikube apply -f payments/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f payments/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f payments/node-port.yaml -n ecommerce
kubectl port-forward service/payments-nodeport-srv --address 0.0.0.0 30003:8003 -n ecommerce
```

It should be accessible at localhost:30003/docs

#### Delivery

- **Apply**:

```sh
kubectl --context=minikube apply -f delivery/deployment.yaml -n ecommerce
kubectl --context=minikube apply -f delivery/service.yaml -n ecommerce
```

- **Access locally via Node-port**:

```sh
kubectl --context=minikube apply -f delivery/node-port.yaml -n ecommerce
kubectl port-forward service/delivery-nodeport-srv --address 0.0.0.0 30004:8004 -n ecommerce
```

It should be accessible at localhost:30004/docs
