##
echo "Mac M1 minikubeにIstioをインストール"
#
minikube delete -p sub-env
minikube start -p sub-env --driver=docker
kubectl config current-context
kubectl config get-contexts
istioctl x precheck
istioctl install --set profile=minimal -y
kubectl label namespace default istio-injection=enabled
kubectl get pods -n istio-system

