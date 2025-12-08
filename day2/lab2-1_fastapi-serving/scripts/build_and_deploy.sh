#!/bin/bash
set -e

echo "============================================================"
echo "  Lab 2-1: FastAPI 빌드 및 배포"
echo "============================================================"

if [ -z "$ECR_REGISTRY" ] || [ -z "$NAMESPACE" ]; then
    echo "ERROR: 환경 변수를 설정하세요"
    echo "export ECR_REGISTRY='<YOUR_ECR>'"
    echo "export NAMESPACE='kubeflow-user01'"
    exit 1
fi

echo "[1/5] Docker 이미지 빌드..."
docker build --platform linux/amd64 -t iris-api:v1 .

echo "[2/5] ECR 로그인..."
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

echo "[3/5] 이미지 푸시..."
docker tag iris-api:v1 $ECR_REGISTRY/mlops-training/iris-api:v1
docker push $ECR_REGISTRY/mlops-training/iris-api:v1

echo "[4/5] Kubernetes 배포..."
envsubst < deployment.yaml | kubectl apply -f -
envsubst < service.yaml | kubectl apply -f -

echo "[5/5] 배포 확인..."
kubectl wait --for=condition=available --timeout=300s deployment/iris-api -n $NAMESPACE

echo ""
echo "✅ 배포 완료!"
kubectl get pods -n $NAMESPACE -l app=iris-api
kubectl get svc iris-api-svc -n $NAMESPACE
