#!/bin/bash

# 1. 眠っているMinikubeを起こす
echo "=== 1. Minikubeを起動しています... ==="
minikube start

# 2. ターミナルの視点をMinikubeに向ける
echo "=== 2. ターミナルのDocker環境をMinikubeに切り替えています... ==="
eval $(minikube docker-env)

# 3. 前日の続きからアプリを起動する
echo "=== 3. 前回（前日）の構成をデプロイしています... ==="
kubectl apply -k k8s/overlays/minikube

# 確認：istio-injection=enabledを確認
kubectl get ns aichat --show-labels

# 💡 再発防止策①：apply直後の「コンテナ初期化のバタつき」をいなすため、10秒だけ安全に進捗を待つ
echo "⏳ クラスターが落ち着くまで10秒間待機しています..."
sleep 10

# 💡 再発防止策②：もし朝イチの重さでコケて（Completed/Crash）いたら、自動で1回叩き起こす
echo "🔄 朝イチの起動を確実にするため、ポッドをローリングアップデート（再起動）します..."
kubectl rollout restart deployment/backend -n aichat
kubectl rollout restart deployment/vectordb -n aichat

# ★ポッドが完全に起動（Running）するのを自動で待つ
echo "=== 4. ポッドが完全に起動（Running）するのを待っています... ==="
kubectl rollout status deployment/backend -n aichat
kubectl rollout status deployment/vectordb -n aichat

# STATUS Running確認
kubectl get pods -n aichat

# 4. Mac->アプリのトンネル開通
echo "=== 5. ポートフォワードを開通します (Ctrl+C で終了) ==="
echo "👉 http://localhost:8080/docs"
echo "👉 http://localhost:8080/"

# 最後に持ってくることで、ターミナルを起動状態のまま維持します
kubectl port-forward -n aichat deploy/backend 8080:8000
