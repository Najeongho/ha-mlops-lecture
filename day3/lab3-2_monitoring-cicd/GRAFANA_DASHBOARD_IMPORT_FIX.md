# 📊 Grafana Dashboard Import 완벽 가이드

## 🔍 현재 상황 분석

진단 결과:
```
✅ Metrics Exporter: Running (데이터 생성 중)
✅ Prometheus Targets: metrics-exporter (1/1 UP)
✅ Prometheus Query: model_mae_score 데이터 존재 ✅
❌ Grafana Dashboard: "No data" 표시
```

**문제의 핵심:** Dashboard는 Import되었지만 DataSource 연결이 안된 상태!

---

## ✅ 완벽한 해결 방법

### 방법 1: 올바른 Import 절차 (추천) ⭐

#### 1단계: 기존 Dashboard 삭제

```
Grafana UI (http://localhost:3000)
→ Dashboards
→ "ML Model Performance Dashboard" 찾기
→ Settings (톱니바퀴 아이콘)
→ Delete dashboard
→ Delete 확인
```

#### 2단계: DataSource 확인

```
Grafana UI
→ Configuration (⚙️)
→ Data Sources
→ "Prometheus" 클릭

확인사항:
✅ Name: Prometheus
✅ URL: http://prometheus.monitoring.svc.cluster.local:9090
✅ Access: Server (default)

"Save & Test" 버튼 클릭
→ ✅ "Data source is working" 확인
```

#### 3단계: Dashboard Import (올바른 방법)

```
1. Grafana UI
   → Dashboards
   → Import
   
2. "Upload JSON file" 클릭
   → dashboards/model-performance-dashboard.json 선택
   
3. ⚠️ **중요!** Import 설정:
   Name: ML Model Performance Dashboard
   Folder: General
   **Prometheus: Prometheus 선택** ⬅️ 반드시 선택!
   
4. Import 버튼 클릭
```

#### 4단계: Dashboard 설정 확인

```
Dashboard 열기
→ 우측 상단 시계 아이콘 (Time Range)
→ "Last 30 minutes" 선택
→ Refresh 버튼 클릭
```

---

### 방법 2: Grafana CLI로 DataSource 재생성

```bash
# 1. Grafana Pod 접속
kubectl exec -it -n monitoring deployment/grafana -- /bin/bash

# 2. DataSource 확인
grafana-cli admin data-source list

# 3. DataSource 추가 (없다면)
cat <<EOF | curl -X POST -H "Content-Type: application/json" \
  -d @- http://admin:admin123@localhost:3000/api/datasources
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus.monitoring.svc.cluster.local:9090",
  "access": "proxy",
  "isDefault": true,
  "uid": "prometheus"
}
EOF

# 4. 재시작
kubectl rollout restart deployment/grafana -n monitoring
```

---

### 방법 3: Dashboard JSON 수정 (고급)

Dashboard JSON에서 datasource를 템플릿 변수로 변경:

```json
{
  "templating": {
    "list": [
      {
        "name": "datasource",
        "type": "datasource",
        "query": "prometheus",
        "current": {
          "text": "Prometheus",
          "value": "prometheus"
        }
      }
    ]
  }
}
```

그런 다음 각 Panel의 datasource를:
```json
"datasource": {
  "type": "prometheus",
  "uid": "${datasource}"
}
```

---

## 🚀 빠른 수정 스크립트

```bash
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
```

---

## 📋 체크리스트

### Import 전
- [ ] Prometheus DataSource 존재 확인
- [ ] DataSource Test 성공
- [ ] Prometheus Query 테스트 (`model_mae_score` 있음)

### Import 시
- [ ] JSON 파일 업로드
- [ ] **Prometheus DataSource 명시적 선택** ⬅️ 가장 중요!
- [ ] Import 버튼 클릭

### Import 후
- [ ] Dashboard 열림
- [ ] Time Range: Last 30 minutes
- [ ] Refresh 버튼 클릭
- [ ] 데이터 표시 확인

---

## 🎯 흔한 실수 Top 3

### 1. DataSource 선택 안함
```
❌ Import 시 Prometheus 선택 안함
→ Panel에서 "No data" 표시
→ 각 Panel마다 수동으로 DataSource 설정 필요

✅ Import 시 Prometheus 명시적 선택
→ 모든 Panel에 자동 적용
```

### 2. Time Range 설정
```
❌ Time Range: "Last 5 minutes"
→ Metrics Exporter가 5분 전에는 데이터 없음
→ "No data"

✅ Time Range: "Last 30 minutes" 이상
→ 충분한 데이터
```

### 3. Auto-refresh 꺼짐
```
❌ Auto-refresh: Off
→ 데이터가 업데이트 안됨

✅ Auto-refresh: 5s or 10s
→ 실시간 업데이트
```

---

## 🔍 문제 진단

### DataSource가 정상인데 "No data"라면

#### 1. Panel Query 확인
```
Panel 클릭
→ Edit (연필 아이콘)
→ Query 탭
→ Query: model_mae_score{...}
→ Run queries (실행 버튼)
→ 하단에 결과 표시되는지 확인
```

#### 2. DataSource 재선택
```
Panel Edit 화면
→ Data source: Prometheus 선택
→ Apply
→ Save dashboard
```

#### 3. Time Range 확장
```
Dashboard 우측 상단
→ Time Range
→ "Last 1 hour" 또는 "Last 6 hours"
→ Apply
```

---

## ✅ 성공 확인

**모든 것이 정상이라면:**

```
Grafana Dashboard:
┌─────────────────────────────────────┐
│ Model MAE Score (Real-time)         │
│ ┌─────────────────────────────────┐ │
│ │   ╭─────╮      v1.0: 0.45       │ │
│ │  ╱       ╲                       │ │
│ │ ╱         ╲    v2.0: 0.34       │ │
│ │╱           ╲                     │ │
│ │             ╲╱                   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Model R² Score                      │
│ ┌─────────────────────────────────┐ │
│ │      ╱─────                      │ │
│ │    ╱       ─────                │ │
│ │  ╱             ─────            │ │
│ │╱                   ────         │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

✅ 실시간 데이터 표시
✅ 범례에 Model A, Model B
✅ 그래프가 움직임 (auto-refresh)
```

---

## 🐛 여전히 "No data"라면

### 최후의 수단: 완전 재설정

```bash
# 1. Grafana 완전 삭제
kubectl delete deployment grafana -n monitoring
kubectl delete configmap grafana-datasources grafana-dashboards-config -n monitoring
kubectl delete service grafana -n monitoring

# 2. 재배포
kubectl apply -f manifests/grafana/

# 3. 대기
kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=120s

# 4. Port-forward
kubectl port-forward -n monitoring svc/grafana 3000:3000

# 5. 브라우저에서 Dashboard Import
# http://localhost:3000 (admin/admin123)
# → Import → Upload JSON
# → **Prometheus 선택** ⬅️ 필수!
```

---

## 📞 추가 도움

### Grafana 로그 확인
```bash
kubectl logs -n monitoring -l app=grafana --tail=100
```

### DataSource API 직접 조회
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
curl http://admin:admin123@localhost:3000/api/datasources
```

### Prometheus에서 직접 쿼리
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl 'http://localhost:9090/api/v1/query?query=model_mae_score' | jq
```

---

© 2024 현대오토에버 MLOps Training  
**Version**: Grafana Dashboard Import 완벽 가이드  
**Status**: ✅ 단계별 해결 방법 제공
