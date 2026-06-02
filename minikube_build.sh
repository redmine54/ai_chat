#!/bin/bash

# 現在のアプリを一旦終了（クリーンアップ）
echo "=== 1. 古いリソースを削除中 ==="
kubectl delete -k k8s/overlays/minikube

# アプリ修正→Dockerイメージ再ビルド
echo "=== 2. Docker環境の切り替えとビルド中 ==="
eval $(minikube docker-env)

# Dockerイメージのビルド
cd src/backend
minikube image build -t backend:local ./

# 再起動（デプロイ）
cd ../..
echo "=== 3. 新しいマニフェストを適用中 ==="
kubectl apply -k k8s/overlays/minikube

# 確認：istio-injection=enabledを確認
kubectl get ns aichat --show-labels

# ★改善ポイント①：ポッドが「完全に起動するまで」自動で待機する
echo "=== 4. ポッドが完全に起動（Running）するのを待っています... ==="
kubectl rollout status deployment/backend -n aichat
kubectl rollout status deployment/vectordb -n aichat

# STATUS Running確認
kubectl get pods -n aichat

# Mac->アプリのトンネル開通
echo "=== 5. ポートフォワードを開通します (Ctrl+C で終了) ==="
echo "👉 http://localhost:8080/docs"
echo "👉 http://localhost:8080/"

# ★改善ポイント②：ここを最後に持ってくることで、ターミナルが起動したまま通信を待ち受けます
kubectl port-forward -n aichat deploy/backend 8080:8000
