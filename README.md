# linkly

A small URL shortener I built to learn the DevOps workflow end to end: write an
app, containerise it, run it on Kubernetes, provision the cloud with Terraform,
and ship it through GitHub Actions with metrics in Grafana.

The app itself is deliberately simple - the point of the project is everything
*around* the app.

![CI](https://github.com/vizzz40/linkly/actions/workflows/ci.yml/badge.svg)

## What's in here

```
app/                FastAPI service + tests
Dockerfile          multi-stage, runs as non-root
docker-compose.yml  app + postgres + prometheus + grafana for local dev
k8s/                kubernetes manifests (app, postgres, monitoring)
terraform/          azure infra (resource group, ACR, AKS)
monitoring/         prometheus config + grafana dashboard
.github/workflows/  CI and CD pipelines
docs/               architecture diagrams
```

See [docs/architecture.md](docs/architecture.md) for the diagrams.

## The API

| Method | Path | What it does |
| --- | --- | --- |
| POST | `/api/shorten` | create a short code for a URL |
| GET | `/{code}` | redirect to the original URL |
| GET | `/api/stats/{code}` | how many times a code was used |
| GET | `/healthz` | liveness probe |
| GET | `/readyz` | readiness probe (checks the DB) |
| GET | `/metrics` | Prometheus metrics |

```bash
curl -X POST localhost:8000/api/shorten -H 'content-type: application/json' \
  -d '{"url": "https://example.com"}'
```

## Run it locally

Just the app (uses a local sqlite file, no setup):

```bash
make install
make run
```

The whole stack with Postgres and monitoring:

```bash
make up
```

- app: http://localhost:8000
- prometheus: http://localhost:9090
- grafana: http://localhost:3000 (dashboard "linkly - service overview")

Run the tests and linter:

```bash
make test
make lint
```

## Run it on Kubernetes (local)

Needs `kind`, `kubectl`, `helm` and a running Docker.

```bash
make kind-up
make kind-deploy
```

For metrics, install the kube-prometheus-stack and apply the monitoring
manifests:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
make monitoring
```

Then port-forward whatever you want to look at, e.g.:

```bash
kubectl port-forward -n linkly svc/linkly 8080:80
```

## Deploy to Azure

Full steps and cost notes are in [terraform/README.md](terraform/README.md).
Short version:

```bash
cd terraform
terraform init -backend-config=backend.hcl
terraform apply
$(terraform output -raw get_credentials_command)
```

### GitHub Actions to Azure (OIDC)

The CD pipeline logs in with OIDC, so there are no long-lived Azure secrets in
GitHub. You create an app registration with a federated credential once:

```bash
az ad app create --display-name linkly-cicd
# create a service principal for the app, then add a federated credential
# scoped to your repo (subject: repo:USERNAME/linkly:ref:refs/heads/main),
# and give it Contributor + AcrPush on the resource group.
```

Then add these repo secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`,
`AZURE_SUBSCRIPTION_ID`. Pushing to `main` builds the image in ACR and rolls it
out to AKS.

## What I learned

- How liveness vs readiness probes actually differ, and why checking the DB in
  liveness is a bad idea (a DB blip would get healthy pods killed).
- Multi-stage Docker builds and why running as a non-root user matters.
- Keeping Prometheus label cardinality under control - bucketing every short
  code under `/{code}` instead of one series per code.
- Terraform remote state, and why you don't want the state file on one laptop.
- Federated (OIDC) auth from GitHub Actions instead of storing cloud secrets.

## Things I'd add next

- Alembic migrations instead of create_all on startup.
- Alerting rules in Prometheus (right now it's just dashboards).
- Move secrets to Azure Key Vault via the CSI driver instead of a committed
  Secret manifest.
- A small frontend instead of curl.
- More tests, especially around code collisions and DB failure paths.

## Known limitations

- The Kubernetes Secret in `k8s/app/secret.yaml` holds demo credentials in
  plain text. Fine for a local demo, not for anything real - see the Key Vault
  note above.
- Postgres runs in-cluster on a single replica with a PVC. It keeps Azure costs
  down but it's not highly available.
