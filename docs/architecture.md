# Architecture

## Delivery pipeline

```mermaid
flowchart LR
    dev[Local dev] -->|git push| gh[GitHub]
    gh --> ci[CI: ruff + pytest + build + scan]
    gh --> cd[CD: build + deploy]
    cd -->|az acr build| acr[(Azure Container Registry)]
    cd -->|kubectl apply / set image| aks[AKS cluster]
    acr -->|image pull| aks
```

## Runtime

```mermaid
flowchart LR
    user[Client] --> ing[NGINX Ingress]
    ing --> app[linkly pods]
    app --> pg[(PostgreSQL)]
    prom[Prometheus] -->|scrape /metrics| app
    graf[Grafana] -->|query| prom
```

## Where each skill lives

| Area | What it does | Files |
| --- | --- | --- |
| App | FastAPI URL shortener with Prometheus metrics | `app/` |
| Containers | Multi-stage, non-root image | `Dockerfile` |
| Local stack | App + Postgres + Prometheus + Grafana | `docker-compose.yml`, `monitoring/` |
| Kubernetes | Deployment, Service, HPA, Ingress, Postgres StatefulSet | `k8s/` |
| Monitoring | ServiceMonitor + Grafana dashboard | `k8s/monitoring/`, `monitoring/grafana/` |
| Infrastructure | Resource group, ACR, AKS, remote state | `terraform/` |
| CI | Lint, test, build, image scan | `.github/workflows/ci.yml` |
| CD | OIDC auth, push to ACR, deploy to AKS | `.github/workflows/cd.yml` |
