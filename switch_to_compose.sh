#!/bin/bash
minikube stop
eval $(minikube docker-env -u)
docker compose up -d
echo "✅ docker compose起動完了"
