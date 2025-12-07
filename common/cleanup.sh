#!/bin/bash
# ============================================================
# cleanup.sh - 실습 환경 정리 스크립트
# ============================================================
#
# 사용법:
#   ./cleanup.sh [namespace]
#
# 예시:
#   ./cleanup.sh kubeflow-user01
# ============================================================

set -e

NAMESPACE="${1:-${NAMESPACE:-kubeflow-user01}}"

echo "============================================================"
echo "  MLOps Training - 환경 정리"
echo "============================================================"
echo ""
echo "  Namespace: ${NAMESPACE}"
echo ""

# 확인
read -p "  ⚠️  모든 리소스를 삭제합니다. 계속하시겠습니까? (y/n): " answer
if [ "$answer" != "y" ]; then
    echo "  취소되었습니다."
    exit 0
fi

echo ""

# ============================================================
# Step 1: InferenceServices 삭제
# ============================================================

echo "[Step 1] InferenceServices 삭제..."

ISVC_COUNT=$(kubectl get inferenceservices -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l || echo "0")

if [ "$ISVC_COUNT" -gt 0 ]; then
    kubectl delete inferenceservices --all -n ${NAMESPACE} 2>/dev/null || true
    echo "  ✅ ${ISVC_COUNT}개 InferenceService 삭제됨"
else
    echo "  ✅ 삭제할 InferenceService 없음"
fi

# ============================================================
# Step 2: Deployments 삭제
# ============================================================

echo ""
echo "[Step 2] Deployments 삭제..."

# 교육용 라벨이 있는 것만 삭제
kubectl delete deployments -l app.kubernetes.io/part-of=mlops-training -n ${NAMESPACE} 2>/dev/null || true

# 특정 패턴의 deployment 삭제
for pattern in "fastapi" "model-server" "california" "project"; do
    kubectl delete deployments -n ${NAMESPACE} $(kubectl get deployments -n ${NAMESPACE} -o name 2>/dev/null | grep ${pattern} || true) 2>/dev/null || true
done

echo "  ✅ Deployments 정리 완료"

# ============================================================
# Step 3: Services 삭제
# ============================================================

echo ""
echo "[Step 3] Services 삭제..."

for pattern in "fastapi" "model-server" "california" "project"; do
    kubectl delete services -n ${NAMESPACE} $(kubectl get services -n ${NAMESPACE} -o name 2>/dev/null | grep ${pattern} || true) 2>/dev/null || true
done

echo "  ✅ Services 정리 완료"

# ============================================================
# Step 4: ConfigMaps 삭제 (교육용만)
# ============================================================

echo ""
echo "[Step 4] ConfigMaps 삭제..."

kubectl delete configmaps -l app.kubernetes.io/part-of=mlops-training -n ${NAMESPACE} 2>/dev/null || true

echo "  ✅ ConfigMaps 정리 완료"

# ============================================================
# Step 5: Secrets 삭제 (교육용만)
# ============================================================

echo ""
echo "[Step 5] Secrets 삭제 (교육용만)..."

kubectl delete secrets -l app.kubernetes.io/part-of=mlops-training -n ${NAMESPACE} 2>/dev/null || true

echo "  ✅ Secrets 정리 완료"

# ============================================================
# Step 6: Completed/Failed Pods 삭제
# ============================================================

echo ""
echo "[Step 6] Completed/Failed Pods 삭제..."

kubectl delete pods --field-selector=status.phase==Succeeded -n ${NAMESPACE} 2>/dev/null || true
kubectl delete pods --field-selector=status.phase==Failed -n ${NAMESPACE} 2>/dev/null || true

echo "  ✅ Pods 정리 완료"

# ============================================================
# Step 7: PVC 정리 (선택적)
# ============================================================

echo ""
echo "[Step 7] PVC 확인..."

PVC_COUNT=$(kubectl get pvc -n ${NAMESPACE} --no-headers 2>/dev/null | wc -l || echo "0")

if [ "$PVC_COUNT" -gt 0 ]; then
    echo "  ⚠️  ${PVC_COUNT}개의 PVC가 있습니다."
    echo "  PVC는 데이터 손실 방지를 위해 자동 삭제하지 않습니다."
    echo "  수동 삭제: kubectl delete pvc <name> -n ${NAMESPACE}"
else
    echo "  ✅ PVC 없음"
fi

# ============================================================
# 요약
# ============================================================

echo ""
echo "============================================================"
echo "  ✅ 정리 완료!"
echo "============================================================"
echo ""
echo "  현재 상태:"
kubectl get all -n ${NAMESPACE} 2>/dev/null | head -20 || true
echo ""
echo "============================================================"
