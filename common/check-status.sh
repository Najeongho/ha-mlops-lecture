#!/bin/bash
# ============================================================
# check-status.sh - 환경 상태 확인 스크립트
# ============================================================
#
# 사용법:
#   ./check-status.sh [namespace]
#
# 예시:
#   ./check-status.sh kubeflow-user01
# ============================================================

NAMESPACE="${1:-${NAMESPACE:-kubeflow-user01}}"

echo "============================================================"
echo "  MLOps Training - 환경 상태 확인"
echo "============================================================"
echo ""
echo "  Namespace: ${NAMESPACE}"
echo "  Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ============================================================
# 1. Kubernetes Connectivity
# ============================================================

echo "============================================================"
echo "  [1] Kubernetes 연결 상태"
echo "============================================================"

if kubectl cluster-info &> /dev/null; then
    echo "  ✅ Kubernetes 클러스터 연결됨"
    kubectl cluster-info | head -2 | sed 's/^/     /'
else
    echo "  ❌ Kubernetes 클러스터에 연결할 수 없습니다."
    echo "     kubectl 설정을 확인하세요."
    exit 1
fi

# ============================================================
# 2. Namespace Check
# ============================================================

echo ""
echo "============================================================"
echo "  [2] Namespace 상태"
echo "============================================================"

if kubectl get namespace ${NAMESPACE} &> /dev/null; then
    echo "  ✅ Namespace '${NAMESPACE}' 존재함"
else
    echo "  ❌ Namespace '${NAMESPACE}'가 존재하지 않습니다."
    echo ""
    echo "  사용 가능한 네임스페이스:"
    kubectl get namespaces | grep -E "^kubeflow|^mlflow" | sed 's/^/     /'
fi

# ============================================================
# 3. Pods
# ============================================================

echo ""
echo "============================================================"
echo "  [3] Pods 상태"
echo "============================================================"

POD_TOTAL=$(kubectl get pods -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)
POD_RUNNING=$(kubectl get pods -n ${NAMESPACE} --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
POD_PENDING=$(kubectl get pods -n ${NAMESPACE} --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)
POD_FAILED=$(kubectl get pods -n ${NAMESPACE} --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)

echo "  Total: ${POD_TOTAL} | Running: ${POD_RUNNING} | Pending: ${POD_PENDING} | Failed: ${POD_FAILED}"
echo ""

if [ "$POD_TOTAL" -gt 0 ]; then
    kubectl get pods -n ${NAMESPACE} --sort-by=.metadata.creationTimestamp 2>/dev/null | tail -10 | sed 's/^/  /'
fi

# ============================================================
# 4. Deployments
# ============================================================

echo ""
echo "============================================================"
echo "  [4] Deployments 상태"
echo "============================================================"

DEPLOY_COUNT=$(kubectl get deployments -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)

if [ "$DEPLOY_COUNT" -gt 0 ]; then
    kubectl get deployments -n ${NAMESPACE} 2>/dev/null | sed 's/^/  /'
else
    echo "  (배포된 Deployment 없음)"
fi

# ============================================================
# 5. Services
# ============================================================

echo ""
echo "============================================================"
echo "  [5] Services 상태"
echo "============================================================"

SVC_COUNT=$(kubectl get services -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l)

if [ "$SVC_COUNT" -gt 0 ]; then
    kubectl get services -n ${NAMESPACE} 2>/dev/null | sed 's/^/  /'
else
    echo "  (Service 없음)"
fi

# ============================================================
# 6. InferenceServices (KServe)
# ============================================================

echo ""
echo "============================================================"
echo "  [6] InferenceServices (KServe)"
echo "============================================================"

ISVC_COUNT=$(kubectl get inferenceservices -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l || echo "0")

if [ "$ISVC_COUNT" -gt 0 ]; then
    kubectl get inferenceservices -n ${NAMESPACE} 2>/dev/null | sed 's/^/  /'
else
    echo "  (배포된 InferenceService 없음)"
fi

# ============================================================
# 7. Kubeflow Pipelines
# ============================================================

echo ""
echo "============================================================"
echo "  [7] Kubeflow Pipelines 상태"
echo "============================================================"

# KFP API 서버 상태
KFP_SVC=$(kubectl get svc -n kubeflow ml-pipeline --no-headers 2>/dev/null | awk '{print $1}')
if [ -n "$KFP_SVC" ]; then
    echo "  ✅ KFP API Server: Running"
else
    echo "  ⚠️ KFP API Server: Not found in kubeflow namespace"
fi

# ============================================================
# 8. MLflow
# ============================================================

echo ""
echo "============================================================"
echo "  [8] MLflow 상태"
echo "============================================================"

MLFLOW_SVC=$(kubectl get svc -n mlflow-system mlflow-server-service --no-headers 2>/dev/null | awk '{print $1}')
if [ -n "$MLFLOW_SVC" ]; then
    echo "  ✅ MLflow Server: Running"
    echo "     Service: mlflow-server-service.mlflow-system.svc.cluster.local:5000"
else
    # mlflow namespace 확인
    MLFLOW_SVC=$(kubectl get svc -A 2>/dev/null | grep mlflow | head -1)
    if [ -n "$MLFLOW_SVC" ]; then
        echo "  ✅ MLflow Server: Found"
        echo "     $MLFLOW_SVC" | sed 's/^/     /'
    else
        echo "  ⚠️ MLflow Server: Not found"
    fi
fi

# ============================================================
# 9. Resource Usage
# ============================================================

echo ""
echo "============================================================"
echo "  [9] Resource Usage"
echo "============================================================"

# 네임스페이스 리소스 사용량
echo "  Namespace Resource Usage:"
kubectl top pods -n ${NAMESPACE} 2>/dev/null | head -10 | sed 's/^/  /' || echo "  (metrics-server 필요)"

# ============================================================
# 10. Recent Events
# ============================================================

echo ""
echo "============================================================"
echo "  [10] Recent Events (최근 5개)"
echo "============================================================"

kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp' 2>/dev/null | tail -6 | sed 's/^/  /' || echo "  (이벤트 없음)"

# ============================================================
# Summary
# ============================================================

echo ""
echo "============================================================"
echo "  📋 요약"
echo "============================================================"
echo ""
echo "  Namespace: ${NAMESPACE}"
echo "  Pods: ${POD_TOTAL} (Running: ${POD_RUNNING})"
echo "  Deployments: ${DEPLOY_COUNT}"
echo "  Services: ${SVC_COUNT}"
echo "  InferenceServices: ${ISVC_COUNT}"
echo ""
echo "============================================================"
echo "  💡 유용한 명령어"
echo "============================================================"
echo ""
echo "  # Pod 로그 확인"
echo "  kubectl logs <pod-name> -n ${NAMESPACE}"
echo ""
echo "  # Pod 상세 정보"
echo "  kubectl describe pod <pod-name> -n ${NAMESPACE}"
echo ""
echo "  # 포트 포워딩"
echo "  kubectl port-forward svc/<service-name> 8080:80 -n ${NAMESPACE}"
echo ""
echo "============================================================"
