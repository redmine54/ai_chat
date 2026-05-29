#!/bin/bash

echo "=== Generating GitHub repository structure ==="

# Root CI file (GitHub Actions 用に workflows ディレクトリを作成)
mkdir -p .github/workflows
touch .github/workflows/github-ci.yml

# CODEOWNERS
touch .github/CODEOWNERS

# base (Kustomize)
mkdir -p base/istio
touch base/kustomization.yaml
touch base/namespace.yaml
touch base/deployment.yaml
touch base/service.yaml
touch base/istio/gateway.yaml
touch base/istio/peer-auth.yaml

# overlays
mkdir -p overlays/{local,development,staging,production}
touch overlays/local/kustomization.yaml
touch overlays/development/kustomization.yaml
touch overlays/staging/kustomization.yaml
touch overlays/production/kustomization.yaml

# terraform
mkdir -p terraform
touch terraform/main.tf
touch terraform/aks.tf
touch terraform/acr.tf
touch terraform/keyvault.tf

# src
mkdir -p src/backend/app
mkdir -p src/frontend
mkdir -p src/vectordb

touch src/backend/Dockerfile
touch src/frontend/Dockerfile
touch src/vectordb/Dockerfile

# tests
mkdir -p tests/{unit,integration,e2e,performance}

# security
mkdir -p security
touch security/trivy.yaml
touch security/sonarqube.yaml
touch security/owasp.yaml

echo "=== GitHub repository structure generated successfully ==="
