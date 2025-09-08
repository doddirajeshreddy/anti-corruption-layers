# Self-Service Database Anti-Corruption Layer (ACL) with GitOps
This project implements a GitOps-driven, self-service Anti-Corruption Layer (ACL) over a legacy PostgreSQL database. It enables microservices to communicate via a dynamic REST API instead of accessing legacy schemas directly. Built with Python, Kubernetes, Helm, and Argo CD, this solution is configurable using Config-as-Code YAML and integrates Git-driven automation.

Local Kubernetes cluster setup (Kind)

Private Docker registry

Helm for deployment

Argo CD (GitOps) for sync automation

Config-as-Code (YAML-based API definitions)




## Folder Structure

```
anti-corruption-layers/
├── app/                       # Python Flask API app
│   ├── app.py                # REST API implementation
│   ├── seeder.sql            # SQL for DB table creation + data seed
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container definition
├── helm/
|   |___ sql/
|   | |__seeder.sql           
│   ├── Chart.yaml            # Helm chart for deploying API & PostgreSQL
│   ├── values.yaml           # Configuration for both API and PostgreSQL
│   ├── configs/
│   │   └── example.yaml      # Config-as-Code for dynamic API endpoints
│   └── templates/            # Kubernetes manifests
│       ├── api-configmap.yaml
│       ├── api-deployment.yaml
│       ├── api-service.yaml
│       ├── postgres-deployment.yaml
│       ├── postgres-services.yaml
│       ├── seed-configmap.yaml
│       └── seed-job.yaml
├── infrastructure/
│   ├── internal-registry/
│   │   └── init.sh           # Local Docker registry setup
│   └── kubernetes/
│       ├── kind-config.yaml  # Kind cluster configuration
│       └── argocd/
│           ├── main.yaml     # Argo CD installation
│           └── application-sets.yaml
└── README.md
```



Prerequisites:

Machine :   Ubuntu 20.04.1 LTS

| Tool         | Version        |
|--------------|----------------|
| Docker       | v20.10.24      |
| Kind         | v0.20.0        |
| kubectl      | v1.27.3        |
| Helm         | v3.18          |
| Argo CD      | v2.10.0        |
| Python       | 3.8.5          |
|Git           | 2.25.1         |
|Curl          | 7.68.0         |

Install Git and Curl using below command
```
  sudo apt install git curl -y
```
## Instructions

### Clone the Repository

```
git clone https://github.com/doddirajeshreddy/anti-corruption-layers.git
cd anti-corruption-layers
```

### Install Prerequisites

```
./setup-prerequisites.sh
```

### Create Local Kind Cluster

```
kind create cluster --name anti-corruption-cluster --config infrastructure/kubernetes/kind-config.yaml
```

### Bootstrap Local Docker Registry

```
bash infrastructure/internal-registry/init.sh
```

### Build and Push the API Image

```
cd app/
docker build -t localhost:5000/anticorruption-api:latest .
docker push localhost:5000/anticorruption-api:latest || true
kind load docker-image localhost:5000/anticorruption-api:latest --name anti-corruption-cluster
```

### Install Argo CD

```
kubectl create namespace argocd
cd ..
kubectl apply -n argocd -f infrastructure/kubernetes/argocd/main.yaml
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### Login to Argo CD

```
# In Another Terminal
argocd login localhost:8080 --username admin --password $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
```

### Create Application in Argo CD

```
kubectl create namespace app
kubectl apply -f infrastructure/kubernetes/argocd/application-sets.yaml

# Port Forward anti corruption app
kubectl port-forward svc/anti-corruption-app-api 3000:3000 -n app

# Port Forward postgres db
kubectl port-forward svc/postgres-service 5432:5432 -n app
```




## (GitOps Behavior)

### Mapping Config (example.yaml) Changes → API Reload

* `helm/configs/example.yaml` defines all API endpoints, queries, and response mappings.
* Referenced in `values.yaml` → injected via ConfigMap → mounted in container
* `api-configmap.yaml` uses `.Files.Get` to pull this dynamically
* Triggers rollout via checksum annotation in `api-deployment.yaml`

### API Code Changes (app.py/Dockerfile) → Rebuild + Push

* Manual rebuild of Docker image
* Push to local registry and reload into Kind
* ArgoCD syncs deployment automatically

### DB IaC Changes → PostgreSQL Redeployment

* Modifications to DB section in `values.yaml` or `postgres-*.yaml`
* Triggers full deployment of PostgreSQL via Argo CD

### DB Schema Initialization

* `seeder.sql` contains `CREATE TABLE` and `INSERT INTO` logic
* Mounted via ConfigMap and executed once by a Job
* To rerun: `kubectl delete job -n app anti-corruption-app-postgres-init`

---

## GitOps Triggers Summary

| Change Trigger           | Result                        |
| ------------------------ | ----------------------------- |
| `configs/example.yaml`   | ConfigMap update → API reload |
| `app.py`, `Dockerfile`   | Manual image rebuild/push     |
| Helm DB templates/values | PostgreSQL redeploy           |
| `seed-configmap.yaml`    | Job runs once → seed database |


### Sample ArgoCD Monitoring Dashboard and Endpoint screenshot


<img width="400" height="200" alt="image" src="https://github.com/user-attachments/assets/b85cdb0a-4067-46d8-aceb-d9ed85343238" />       
<img width="400" height="200" alt="image" src="https://github.com/user-attachments/assets/b7bd1306-9276-4983-9d34-a385d654dc83" />





