echo "re-build of minikube"
echo "minikubeのdocker-envを解除"
eval $(minikube docker-env -u)

# 2. 再ビルド

docker compose build --no-cache
docker compose up -d

echo "re-build完了, http://localhost:8000/api/specs "

