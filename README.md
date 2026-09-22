# Task Manager Microservices

A simple microservice-based Task Manager application developed for the Applied Cloud Computing and Big Data assignment.

## Architecture

The application consists of:

- **Task Service** – REST API for creating, reading and deleting tasks.
- **User Service** – REST API for managing users.
- **MongoDB** – persistent database running as a separate Kubernetes deployment.
- **Kubernetes** – deploys and manages all application components.

The Task Service consumes the User Service through its REST API.

## Technologies

- Python
- Flask
- MongoDB
- Docker
- Kubernetes
- Docker Hub
- GitHub

## Docker Hub Images

- `mouhannad86/task-service:3.0`
- `mouhannad86/user-service:1.0`

## Kubernetes

The application is deployed in the `task-manager` namespace.

MongoDB uses a PersistentVolumeClaim (PVC) to preserve data when the MongoDB pod is restarted.

Task Service and User Service are deployed independently and can be horizontally scaled.

## REST APIs

### Task Service

- GET `/tasks`
- GET `/tasks/<id>`
- POST `/tasks`
- DELETE `/tasks/<id>`
- GET `/tasks/<id>/user`
- GET `/health`

### User Service

- GET `/users`
- GET `/users/<id>`
- POST `/users`
- DELETE `/users/<id>`
- GET `/health`

The Task Service consumes the User Service REST API to retrieve the user associated with a task.

## Running with Kubernetes

Apply the Kubernetes manifests:

```text
kubectl apply -f kubernetes/mongodb-storage.yaml
kubectl apply -f kubernetes/mongodb.yaml
kubectl apply -f kubernetes/user-service.yaml
kubectl apply -f kubernetes/task-service.yaml
```

Check the deployment:

```text
kubectl get pods -n task-manager
```

Expected components:

- MongoDB
- Task Service
- User Service

## Local Access

For local browser/API access, use:

```text
kubectl port-forward service/task-service 8080:5000 -n task-manager
```

Then open:

`http://localhost:8080/tasks`

## Persistence

MongoDB uses a Kubernetes PersistentVolumeClaim.

The application was tested by deleting the MongoDB pod and allowing Kubernetes to create a new pod. Existing tasks remained available after the restart, demonstrating persistent storage.

## Horizontal Scaling

Task Service and User Service can be scaled independently using Kubernetes.

Example:

```text
kubectl scale deployment task-service --replicas=2 -n task-manager
kubectl scale deployment user-service --replicas=2 -n task-manager
```

## Project Repository

https://github.com/mouhannad1986/task-manager-microservices