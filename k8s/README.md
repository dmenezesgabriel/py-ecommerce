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
kubectl --context=minikube delete -f namespace.yaml
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

#### Create databases

- **Apply**:

```sh
kubectl --context=minikube kustomize postgres -n ecommerce
kubectl --context=minikube apply -k postgres -n ecommerce
kubectl logs job/run-postgres-init-scripts -n ecommerce
```

```sh
kubectl --context=minikube delete -k postgres -n ecommerce
```
