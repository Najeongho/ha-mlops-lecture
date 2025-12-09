#!/bin/bash
# grafana-dashboard-fix.sh

echo "🔧 Grafana Dashboard 완전 수정..."

# 1. Grafana 재시작 (ConfigMap 새로고침)
echo "Step 1: Restarting Grafana..."
kubectl rollout restart deployment/grafana -n monitoring
sleep 30

# 2. Grafana 준비 대기
echo "Step 2: Waiting for Grafana to be ready..."
kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=60s

# 3. Port-forward
echo "Step 3: Port-forwarding Grafana..."
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
PF_PID=$!
sleep 5

# 4. DataSource 테스트
echo "Step 4: Testing DataSource..."
curl -s http://admin:admin123@localhost:3000/api/datasources/uid/prometheus | jq '.name, .url'

# 5. Dashboard 목록
echo "Step 5: Current dashboards..."
curl -s http://admin:admin123@localhost:3000/api/search?type=dash-db | jq '.[] | {title, uid}'

kill $PF_PID

echo ""
echo "✅ Next Steps:"
echo "1. kubectl port-forward -n monitoring svc/grafana 3000:3000"
echo "2. Open http://localhost:3000 (admin/admin123)"
echo "3. Import dashboards/model-performance-dashboard.json"
echo "4. SELECT 'Prometheus' as Data Source during import!"
