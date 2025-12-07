#!/bin/bash
# ============================================================
# deploy.sh - KServe InferenceService 배포 스크립트
# ============================================================
#
# 사용법:
#   ./deploy.sh [namespace] [model-name]
#
# 예시:
#   ./deploy.sh kubeflow-user01 california-model
# ============================================================

set -e

# 기본값 설정
NAMESPACE="${1:-${NAMESPACE:-kubeflow-user01}}"
MODEL_NAME="${2:-california-model}"
S3_BUCKET="${S3_BUCKET:-mlops-training-models}"

echo "============================================================"
echo "  KServe InferenceService 배포"
echo "============================================================"
echo ""
echo "  Namespace: ${NAMESPACE}"
echo "  Model Name: ${MODEL_NAME}"
echo "  S3 Bucket: ${S3_BUCKET}"
echo ""

# ============================================================
# Step 1: 기존 InferenceService 확인
# ============================================================

echo "[Step 1] 기존 InferenceService 확인..."

if kubectl get inferenceservice ${MODEL_NAME} -n ${NAMESPACE} &> /dev/null; then
    echo "  ⚠️  기존 InferenceService가 존재합니다."
    read -p "  삭제하고 재배포할까요? (y/n): " answer
    if [ "$answer" = "y" ]; then
        kubectl delete inferenceservice ${MODEL_NAME} -n ${NAMESPACE}
        echo "  ✅ 기존 InferenceService 삭제됨"
        sleep 5
    else
        echo "  배포 취소됨"
        exit 0
    fi
else
    echo "  ✅ 기존 InferenceService 없음"
fi

# ============================================================
# Step 2: YAML 파일 생성
# ============================================================

echo ""
echo "[Step 2] InferenceService YAML 생성..."

cat > /tmp/inference-service-deploy.yaml << EOF
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: ${MODEL_NAME}
  namespace: ${NAMESPACE}
  annotations:
    autoscaling.knative.dev/minScale: "1"
    autoscaling.knative.dev/maxScale: "3"
spec:
  predictor:
    sklearn:
      storageUri: "s3://${S3_BUCKET}/${MODEL_NAME}/model"
      resources:
        requests:
          cpu: "100m"
          memory: "256Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
EOF

echo "  ✅ YAML 파일 생성: /tmp/inference-service-deploy.yaml"

# ============================================================
# Step 3: 배포
# ============================================================

echo ""
echo "[Step 3] InferenceService 배포..."

kubectl apply -f /tmp/inference-service-deploy.yaml

echo "  ✅ InferenceService 배포 요청됨"

# ============================================================
# Step 4: 상태 확인
# ============================================================

echo ""
echo "[Step 4] 배포 상태 확인 중... (최대 3분 대기)"

TIMEOUT=180
INTERVAL=10
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    STATUS=$(kubectl get inferenceservice ${MODEL_NAME} -n ${NAMESPACE} -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
    
    if [ "$STATUS" = "True" ]; then
        echo ""
        echo "  ✅ InferenceService READY!"
        break
    fi
    
    echo "  ⏳ 대기 중... (${ELAPSED}/${TIMEOUT}s) - Status: ${STATUS}"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$STATUS" != "True" ]; then
    echo ""
    echo "  ⚠️  타임아웃! 수동으로 상태를 확인하세요:"
    echo "     kubectl get inferenceservice ${MODEL_NAME} -n ${NAMESPACE}"
    echo "     kubectl describe inferenceservice ${MODEL_NAME} -n ${NAMESPACE}"
fi

# ============================================================
# Step 5: 엔드포인트 정보
# ============================================================

echo ""
echo "[Step 5] 엔드포인트 정보"
echo "============================================================"

URL=$(kubectl get inferenceservice ${MODEL_NAME} -n ${NAMESPACE} -o jsonpath='{.status.url}' 2>/dev/null || echo "N/A")

echo "  Internal URL: ${URL}"
echo ""
echo "  테스트 방법:"
echo ""
echo "  # 포트 포워딩"
echo "  kubectl port-forward svc/${MODEL_NAME}-predictor-default -n ${NAMESPACE} 8080:80"
echo ""
echo "  # API 호출"
echo "  curl -X POST http://localhost:8080/v1/models/${MODEL_NAME}:predict \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"instances\": [[8.3252, 41.0, 6.984, 1.024, 322.0, 2.556, 37.88, -122.23]]}'"
echo ""
echo "============================================================"
echo "  ✅ 배포 스크립트 완료!"
echo "============================================================"
