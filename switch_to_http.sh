#!/bin/bash
echo "🛑 minikube tunnelを停止してください（Ctrl+C）"
kubectl port-forward -n aichat deploy/backend 8090:8000
echo "👉 http://localhost:8090/swagger/docs"
