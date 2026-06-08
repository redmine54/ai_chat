echo "re-build of minikube"
# 1. minikubeのDockerを使用
eval $(minikube docker-env)

# 2. 再ビルド
docker build -t aichat:latest -f src/backend/Dockerfile .

# 3. Pod再起動
kubectl rollout restart deployment/backend -n aichat

# 4. 完了待ち
kubectl rollout status deployment/backend -n aichat

echo "re-build完了, http://localhost:8090/api/specs "

