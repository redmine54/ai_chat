#!/bin/bash
echo "🔒 自己証明書（aichat-tls）を作成・設定します"

# 証明書の保存フォルダ作成
mkdir -p base/istio/certs

# 自己署名証明書の作成
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout base/istio/certs/aichat.key \
  -out base/istio/certs/aichat.crt \
  -subj "/CN=localhost/O=aichat"

# K8sのSecretに登録
kubectl create secret tls aichat-tls \
  --cert=base/istio/certs/aichat.crt \
  --key=base/istio/certs/aichat.key \
  -n istio-system
# 確認
kubectl get secret aichat-tls -n istio-system

echo "✅ 証明書の作成・設定が完了しました"
