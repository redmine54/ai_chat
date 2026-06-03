#!/bin/bash
minikube stop
docker compose up -d
echo "✅ docker compose起動完了"
