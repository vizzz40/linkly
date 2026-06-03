# linkly

![CI](https://github.com/vizzz40/linkly/actions/workflows/ci.yml/badge.svg)

A URL shortener I built to practice the whole DevOps workflow end to end, not just
the app: containers, Kubernetes, Terraform, CI/CD and monitoring.

## Stack

- FastAPI + PostgreSQL, Prometheus metrics at `/metrics`
- Docker (multi-stage, non-root) + docker-compose for local dev
- Kubernetes manifests: Deployment, Service, HPA, Ingress, Postgres StatefulSet
- Prometheus + Grafana dashboard
- Terraform for Azure (AKS + ACR)
- GitHub Actions for CI and CD

Diagrams are in `docs/architecture.md`.

## API

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/shorten` | create a short code for a URL |
| GET | `/{code}` | redirect to the original URL |
| GET | `/api/stats/{code}` | usage count for a code |
| GET | `/healthz`, `/readyz` | health probes |
| GET | `/metrics` | prometheus metrics |

## Run locally

The whole stack (app + postgres + prometheus + grafana):

    make up

App on `:8000` (`/docs` for the API), Prometheus on `:9090`, Grafana on `:3000`.
Tests and linting:

    make test
    make lint

## Run on Kubernetes (local)

    make kind-up
    make kind-deploy

Monitoring uses the kube-prometheus-stack Helm chart; see `k8s/` and the Makefile.

## Azure

`terraform/` provisions AKS + ACR (see `terraform/README.md`). The CD workflow
builds the image to ACR and deploys to AKS using OIDC, so there are no cloud
secrets stored in GitHub.

## What I learned

- liveness vs readiness probes, and why checking the DB in liveness is a bad idea
- keeping Prometheus label cardinality under control
- Terraform remote state, and why you don't keep state on one laptop
- OIDC auth from GitHub Actions instead of storing cloud secrets

## Known limitations

- the Kubernetes Secret holds demo credentials in plain text; real use should be a secrets manager
- Postgres runs in-cluster on a single replica, so it isn't highly available

## Next steps

- Alembic migrations instead of create_all on startup
- Prometheus alert rules, not just dashboards
- move secrets to Azure Key Vault
