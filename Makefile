.PHONY: install run test lint fmt docker-build up down kind-up load-image kind-deploy monitoring tf-init tf-apply tf-destroy clean

install:
	pip install -r app/requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff check --fix .
	ruff format .

docker-build:
	docker build -t linkly:latest .

up:
	docker compose up --build

down:
	docker compose down -v

kind-up:
	kind create cluster --name linkly

load-image: docker-build
	kind load docker-image linkly:latest --name linkly

kind-deploy: load-image
	kubectl apply -f k8s/app -f k8s/postgres

monitoring:
	kubectl apply -f k8s/monitoring

tf-init:
	cd terraform && terraform init -backend-config=backend.hcl

tf-apply:
	cd terraform && terraform apply

tf-destroy:
	cd terraform && terraform destroy

clean:
	docker compose down -v || true
	kind delete cluster --name linkly || true
