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
kubectl port-forward service/postgres --address 0.0.0.0 30432:5432 -n ecommerce
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
kubectl port-forward service/mongo --address 0.0.0.0 30433:27017 -n ecommerce
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
kubectl port-forward service/rabbitmq --address 0.0.0.0 30434:15672 -n ecommerce
```

It should be accessible at localhost:30434
