#!/bin/bash
# ============================================================
# grafana-access.sh - Grafana 대시보드 접속 스크립트
# ============================================================
#
# 사용법:
#   ./grafana-access.sh
#
# 접속 정보:
#   URL: http://localhost:3000
#   Username: admin
#   Password: 제공된 비밀번호
# ============================================================

set -e

GRAFANA_NAMESPACE="${GRAFANA_NAMESPACE:-monitoring}"
LOCAL_PORT="${LOCAL_PORT:-3000}"

echo "============================================================"
echo "  Grafana Dashboard 접속"
echo "============================================================"
echo ""

# Grafana Pod 상태 확인
echo "[Step 1] Grafana Pod 상태 확인..."

GRAFANA_POD=$(kubectl get pods -n ${GRAFANA_NAMESPACE} -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$GRAFANA_POD" ]; then
    echo "  ❌ Grafana Pod를 찾을 수 없습니다."
    echo ""
    echo "  💡 다른 네임스페이스를 확인하세요:"
    echo "     kubectl get pods -A | grep grafana"
    exit 1
fi

echo "  ✅ Grafana Pod: ${GRAFANA_POD}"

# Pod 상태 확인
POD_STATUS=$(kubectl get pod ${GRAFANA_POD} -n ${GRAFANA_NAMESPACE} -o jsonpath='{.status.phase}')
echo "  ✅ Status: ${POD_STATUS}"

if [ "$POD_STATUS" != "Running" ]; then
    echo "  ⚠️  Grafana Pod가 Running 상태가 아닙니다."
    exit 1
fi

# 포트 포워딩 실행
echo ""
echo "[Step 2] 포트 포워딩 시작..."
echo ""
echo "  🌐 브라우저에서 접속하세요:"
echo "     http://localhost:${LOCAL_PORT}"
echo ""
echo "  📋 로그인 정보:"
echo "     Username: admin"
echo "     Password: [제공된 비밀번호]"
echo ""
echo "  ⚠️  종료하려면 Ctrl+C를 누르세요."
echo ""
echo "============================================================"

# 포트 포워딩 (foreground)
kubectl port-forward svc/grafana -n ${GRAFANA_NAMESPACE} ${LOCAL_PORT}:3000
