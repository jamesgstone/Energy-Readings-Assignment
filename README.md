*Energy Readings Pipeline*
This project implements a distributed energy data pipeline designed to ingest, process, and store meter readings at scale. The architecture uses a decoupled producer-consumer pattern via Redis Streams and is built to run on Kubernetes with automated scaling.

**Architecture Overvie**
The system consists of three primary components:

Ingestion API (FastAPI): A high-performance REST entry point that validates incoming JSON payloads and publishes them to a Redis Stream named energy_readings.

Redis: Serves as the message broker using Streams for reliable delivery and as the primary data store for processed site data.

Processing Service: An asynchronous consumer that reads from a Redis Consumer Group. It ensures "at-least-once" delivery by acknowledging messages (XACK) only after they are successfully persisted into site-specific lists.

KEDA Scaler: A Kubernetes-native autoscaler that monitors the Redis Stream lag and dynamically adjusts the number of processing pods based on the volume of unread messages.

**Deployment Instructions**
1. Containerization
Build the images locally before deploying to the cluster. Ensure you are in the project root:

# Ingestion API
docker build -t ingestion-api:v1 "./Ingestion API"

# Processing Service
docker build -t processing-service:v1 "./Processing Svc"
2. Kubernetes Installation (Helm)
The deployment is managed via a Helm chart located in the charts/pipeline directory. This handles the creation of Deployments, Services (with proper Assignment-ID labels), and the KEDA ScaledObject.

# From the project root
helm install energy-pipeline ./charts/pipeline
Validation and Testing
Step 1: Ingest Data
Push a sample reading to the API using the NodePort 30001. 

curl -X POST http://localhost:30001/readings \
-H "Content-Type: application/json" \
-d '{
  "site id": "site-101",
  "device id": "meter-01",
  "power_reading": 1250.5,
  "timestamp": "2024-01-15T12:00:00Z"
}'
Step 2: Verify Processing
The processing service internally stores the data. You can verify the data is processed by checking the logs or querying the internal processing service endpoint:


# Example if using port-forward to the processing service (port 8000)
curl http://localhost:8000/sites/site-101/readings
Scaling Logic: The ScaledObject is configured to trigger scaling when the pending message count in the energy_readings stream exceeds 5. It is configured with a minReplicaCount of 1 and a maxReplicaCount of 5.

Networking: The Ingestion API is exposed via a NodePort (30001) for external access, while Redis and the Processor communicate over the internal ClusterIP service (redis-service).

Environment Variables: Configuration (Host, Port, Stream names) is injected via Kubernetes env vars, allowing for easy environment-specific overrides in the values.yaml file.

Repository Structure
Ingestion API/ - FastAPI source code, requirements.txt and Dockerfile.

Processing Svc/ - Async consumer source code, requirements.txt and Dockerfile.

charts/pipeline/ - Helm templates (Deployment, Service, ScaledObject) and configuration values.

CI-CD/ - gitlab-ci.yml

-----------------------------------------------------
## Development Status & Notes


**Current Testing Status:**
* **Logic & Integration:** Verified locally using Postman, Docker, and Redis.
* **Kubernetes/Helm:** The Helm charts and KEDA configurations are written and structured, though final cluster-wide verification is pending the installation of Minikube and the Helm CLI on this environment.

**Next Steps:**
I intend to complete the bonus requirement
and will push the updates to GitHub. My primary focus was to deliver a functional, high-quality core requirement within a short timeframe.

**CI/CD Pipeline Note:** > The current GitLab (GitHub action can be used) workflow focuses on validation (helm lint) and image construction (docker build). In a real-world scenario, a docker push step would be integrated to ship these images to a registry like Docker Hub or Artifactory.

## GitOps Integration (ArgoCD)
To move towards a full GitOps model, this project is structured to be easily integrated with **ArgoCD**:

* **Automated Sync:** An ArgoCD `Application` manifest can be pointed at the `charts/pipeline` directory.
* **Continuous Deployment:** Once the CI pipeline pushes a new image tag to the registry, ArgoCD will detect the change in `values.yaml` (or via an image updater) and automatically pull the latest version into the cluster.
* **Self-Healing:** ArgoCD will ensure that any manual changes made to the cluster (drift) are automatically reverted to match the state defined in this repository.

> **Note:** If needed, an `application.yaml` manifest for ArgoCD can be provided to define the destination cluster and sync policy.