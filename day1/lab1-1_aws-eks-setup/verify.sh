#!/bin/bash
# ============================================================
# verify.sh - Lab 1-1 환경 설정 검증 스크립트
# ============================================================

echo "============================================================"
echo "  Lab 1-1: AWS EKS 환경 설정 검증"
echo "============================================================"

PASS=0
FAIL=0

# Test 1: AWS CLI 자격 증명
echo ""
echo "[Test 1] AWS CLI Credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "  ✅ PASS - AWS CLI configured"
    ((PASS++))
else
    echo "  ❌ FAIL - AWS CLI not configured"
    ((FAIL++))
fi

# Test 2: kubectl 연결
echo ""
echo "[Test 2] kubectl Connection..."
if kubectl cluster-info &> /dev/null; then
    echo "  ✅ PASS - kubectl connected to cluster"
    ((PASS++))
else
    echo "  ❌ FAIL - kubectl not connected"
    ((FAIL++))
fi

# Test 3: 노드 확인
echo ""
echo "[Test 3] Cluster Nodes..."
NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
if [ "$NODE_COUNT" -gt 0 ]; then
    echo "  ✅ PASS - Found ${NODE_COUNT} nodes"
    ((PASS++))
else
    echo "  ❌ FAIL - No nodes found"
    ((FAIL++))
fi

# Test 4: 네임스페이스 접근
echo ""
echo "[Test 4] Namespace Access..."
NAMESPACE="${NAMESPACE:-kubeflow-user01}"
if kubectl get pods -n ${NAMESPACE} &> /dev/null; then
    echo "  ✅ PASS - Can access namespace ${NAMESPACE}"
    ((PASS++))
else
    echo "  ❌ FAIL - Cannot access namespace ${NAMESPACE}"
    ((FAIL++))
fi

# 결과 요약
echo ""
echo "============================================================"
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo "============================================================"

if [ $FAIL -eq 0 ]; then
    echo "  🎉 All tests passed! You're ready for the next lab."
    exit 0
else
    echo "  ⚠️  Some tests failed. Please check the issues above."
    exit 1
fi
