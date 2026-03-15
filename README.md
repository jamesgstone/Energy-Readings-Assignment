Energy Readings Pipeline
This project implements a distributed energy data pipeline designed to ingest, process, and store meter readings at scale. The architecture uses a decoupled producer-consumer pattern via Redis Streams and is built to run on Kubernetes with automated scaling.

Architecture Overview
The system consists of three primary components:

Ingestion API (FastAPI): A high-performance REST entry point that validates incoming JSON payloads and publishes them to a Redis Stream named energy_readings.

Redis: Serves as the message broker using Streams for reliable delivery and as the primary data store for processed site data.

Processing Service: An asynchronous consumer that reads from a Redis Consumer Group. It ensures "at-least-once" delivery by acknowledging messages (XACK) only after they are successfully persisted into site-specific lists.

KEDA Scaler: A Kubernetes-native autoscaler that monitors the Redis Stream lag and dynamically adjusts the number of processing pods based on the volume of unread messages.

Deployment Instructions
1. Containerization
Build the images locally before deploying to the cluster. Ensure you are in the project root:

Bash
# Ingestion API
docker build -t ingestion-api:v1 "./Ingestion API"

# Processing Service
docker build -t processing-service:v1 "./Processing Svc"
2. Kubernetes Installation (Helm)
The deployment is managed via a Helm chart located in the charts/pipeline directory. This handles the creation of Deployments, Services, and the KEDA ScaledObject.

Bash
cd charts
helm install energy-pipeline ./pipeline
Validation and Testing
Once the pods are healthy, you can verify the end-to-end flow using curl.

Step 1: Ingest Data (Port 8000)
Push a sample reading to the API. Note that the schema supports keys with spaces (e.g., "site id") as per the requirement.

Bash
curl -X POST http://localhost:8000/readings \
-H "Content-Type: application/json" \
-d '{
  "site id": "site-101",
  "device id": "meter-01",
  "power_reading": 1250.5,
  "timestamp": "2024-01-15T12:00:00Z"
}'
Step 2: Verify Processing (Port 8001)
Query the Processing Service to confirm the data was moved from the Stream to the site-specific storage:

Bash
curl http://localhost:8001/sites/site-101/readings
Operational Details
Concurrency: Both services are built using Python's asyncio and redis.asyncio to handle high I/O throughput without blocking.

Scaling Logic: The ScaledObject is configured to trigger scaling when the pending message count in the energy_readings stream exceeds 5. It is configured with a minReplicaCount of 1 and a maxReplicaCount of 5.

Networking: The Ingestion API is exposed via a NodePort (30001) for external access, while Redis and the Processor communicate over the internal ClusterIP service (redis-service).

Environment Variables: Configuration (Host, Port, Stream names) is injected via Kubernetes env vars, allowing for easy environment-specific overrides in the values.yaml file.

Repository Structure
Ingestion API/ - FastAPI source code and Dockerfile.

Processing Svc/ - Async consumer source code and Dockerfile.

charts/pipeline/ - Helm templates (Deployment, Service, ScaledObject) and configuration values.