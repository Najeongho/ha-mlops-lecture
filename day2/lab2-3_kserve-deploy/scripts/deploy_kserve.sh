#!/bin/bash
# ============================================================
# Lab 2-3: KServe InferenceService 배포 스크립트
# ============================================================
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "============================================================"
echo "  KServe InferenceService 배포"
echo "============================================================"

# 네임스페이스 설정
if [ -f "/var/run/secrets/kubernetes.io/serviceaccount/namespace" ]; then
    NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
elif [ -n "$USER_NAMESPACE" ]; then
    NAMESPACE="$USER_NAMESPACE"
else
    NAMESPACE="kubeflow-user-example-com"
    echo -e "${YELLOW}⚠️  네임스페이스를 확인하세요: $NAMESPACE${NC}"
fi

# 모델 설정
MODEL_NAME=${MODEL_NAME:-"california-model"}
S3_BUCKET=${S3_BUCKET:-"mlops-training-user01"}

echo "📁 네임스페이스: $NAMESPACE"
echo "🤖 모델명: $MODEL_NAME"
echo ""

# Storage URI 확인
if [ -z "$STORAGE_URI" ]; then
    echo -e "${YELLOW}⚠️  STORAGE_URI가 설정되지 않았습니다.${NC}"
    echo ""
    echo "S3에서 모델 경로를 확인하세요:"
    echo "  aws s3 ls s3://$S3_BUCKET/mlflow-artifacts/ --recursive | grep MLmodel"
    echo ""
    echo "그 다음 환경변수를 설정하세요:"
    echo "  export STORAGE_URI='s3://$S3_BUCKET/mlflow-artifacts/EXPERIMENT_ID/RUN_ID/artifacts/model'"
    echo ""
    exit 1
fi

echo "📦 Storage URI: $STORAGE_URI"
echo ""

# 기존 InferenceService 삭제 (있으면)
echo "🗑️  기존 InferenceService 확인 중..."
if kubectl get inferenceservice $MODEL_NAME -n $NAMESPACE &>/dev/null; then
    echo "  기존 InferenceService 삭제 중..."
    kubectl delete inferenceservice $MODEL_NAME -n $NAMESPACE --wait=true
    sleep 5
fi

# InferenceService YAML 생성 및 적용
echo ""
echo "📝 InferenceService 생성 중..."

cat <<EOF | kubectl apply -f -
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: $MODEL_NAME
  namespace: $NAMESPACE
  annotations:
    # ⚠️ 중요: Istio sidecar 비활성화 (RBAC 403 에러 방지)
    sidecar.istio.io/inject: "false"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "$STORAGE_URI"
      resources:
        requests:
          cpu: "500m"
          memory: "1Gi"
        limits:
          cpu: "1"
          memory: "2Gi"
EOF

echo -e "${GREEN}✅ InferenceService 생성 완료${NC}"
echo ""

# 배포 대기
echo "⏳ 배포 대기 중 (최대 5분)..."
echo "   (보통 2-3분 소요)"
echo ""

TIMEOUT=300
START_TIME=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo -e "${RED}❌ 타임아웃: ${TIMEOUT}초 초과${NC}"
        echo ""
        echo "상태 확인:"
        kubectl describe inferenceservice $MODEL_NAME -n $NAMESPACE | tail -30
        exit 1
    fi
    
    # 상태 확인
    READY=$(kubectl get inferenceservice $MODEL_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
    REASON=$(kubectl get inferenceservice $MODEL_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].reason}' 2>/dev/null || echo "Pending")
    
    if [ "$READY" == "True" ]; then
        echo ""
        echo -e "${GREEN}✅ InferenceService Ready! (${ELAPSED}초 소요)${NC}"
        break
    elif [ "$READY" == "False" ]; then
        echo -e "${RED}❌ 배포 실패: $REASON${NC}"
        echo ""
        echo "로그 확인:"
        kubectl logs -n $NAMESPACE -l serving.knative.dev/configuration=${MODEL_NAME}-predictor -c storage-initializer --tail=20 2>/dev/null || echo "로그 없음"
        exit 1
    else
        printf "  ⏳ Status: %s | Reason: %s (%ds)\r" "$READY" "$REASON" "$ELAPSED"
    fi
    
    sleep 10
done

# 최종 상태 출력
echo ""
echo "============================================================"
echo "  배포 완료"
echo "============================================================"
echo ""
kubectl get inferenceservice $MODEL_NAME -n $NAMESPACE
echo ""

# Pod 상태
echo "📋 Pod 상태:"
kubectl get pods -n $NAMESPACE -l serving.knative.dev/configuration=${MODEL_NAME}-predictor
echo ""

# 내부 URL
echo "🔗 클러스터 내부 URL:"
echo "   http://${MODEL_NAME}-predictor.${NAMESPACE}.svc.cluster.local/v1/models/${MODEL_NAME}:predict"
echo ""
echo -e "${GREEN}✅ 배포 완료! test_inference.sh로 테스트하세요.${NC}"
