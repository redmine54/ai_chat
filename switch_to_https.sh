#!/bin/bash
echo "🔒 HTTPS（minikube tunnel）モードで起動します"
minikube tunnel
echo "👉 https://localhost/docs"
# 注意: httpsは証明書（aichat-tls）が必要です
