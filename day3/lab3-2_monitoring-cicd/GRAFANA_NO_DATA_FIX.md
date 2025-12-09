# 📊 Grafana "No Data" 문제 완전 해결

## ❌ 문제 상황

Grafana Dashboard에 계속 "No data" 표시:

```
✅ metrics-exporter: Running
✅ Prometheus: Running
❌ Grafana Dashboard: No data
```

## 🔍 진단 방법

### 1단계: Metrics Exporter 확인

```bash
# Pod 상태
kubectl get pods -n monitoring -l app=metrics-exporter

# 예상 출력:
# NAME                               READY   STATUS    RESTARTS
# metrics-exporter-xxx               1/1     Running   0

# 로그 확인
kubectl logs -n monitoring -l app=metrics-exporter --tail=20

# 예상 출력:
# ✅ Metrics server started: http://localhost:8000/metrics
# [0030s] Generated 60 metric updates
```

### 2단계: Metrics 직접 확인

```bash
# Port-forward
kubectl port-forward -n monitoring svc/metrics-exporter 8000:8000 &

# Metrics 조회
curl http://localhost:8000/metrics | grep model_mae_score

# 예상 출력:
# model_mae_score{model_name="california-housing",version="v1.0"} 0.42
# model_mae_score{model_name="california-housing",version="v2.0"} 0.37
```

**✅ 정상**: 메트릭 데이터 존재  
**❌ 비정상**: 데이터 없거나 에러

---

### 3단계: Prometheus Targets 확인

```bash
# Prometheus Port-forward
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

브라우저에서 http://localhost:9090/targets 접속:

**확인사항:**
```
Job: metrics-exporter
State: UP ✅ 또는 DOWN ❌
Last Scrape: 15s ago
Endpoint: http://metrics-exporter.monitoring.svc.cluster.local:8000/metrics
```

**UP 상태인데 Grafana에 데이터 없음** → 4단계로  
**DOWN 상태** → Prometheus 설정 문제 → 해결 방법 1

---

### 4단계: Prometheus Query 테스트

Prometheus UI에서 직접 쿼리:

```
http://localhost:9090/graph

Query:
model_mae_score

Execute 버튼 클릭
```

**✅ 데이터 존재**: Prometheus는 정상, Grafana 연결 문제 → 해결 방법 2  
**❌ 데이터 없음**: Prometheus scrape 문제 → 해결 방법 1

---

## ✅ 해결 방법

### 해결 방법 1: Prometheus Scrape 문제

#### 1-1. Prometheus ConfigMap 확인

```bash
kubectl get configmap prometheus-config -n monitoring -o yaml | grep -A 10 "metrics-exporter"
```

**예상 출력:**
```yaml
- job_name: 'metrics-exporter'
  static_configs:
    - targets: ['metrics-exporter.monitoring.svc.cluster.local:8000']
  scrape_interval: 15s
  scrape_timeout: 10s
```

**없거나 잘못되었다면:**

```bash
# ConfigMap 수정
kubectl edit configmap prometheus-config -n monitoring

# 또는 재배포
kubectl apply -f manifests/prometheus/02-prometheus-config.yaml

# Prometheus 재시작
kubectl rollout restart deployment/prometheus -n monitoring
```

#### 1-2. Service 확인

```bash
kubectl get svc metrics-exporter -n monitoring

# 예상 출력:
# NAME               TYPE        CLUSTER-IP      PORT(S)
# metrics-exporter   ClusterIP   10.100.x.x      8000/TCP
```

**Service가 없다면:**
```bash
kubectl apply -f manifests/metrics-exporter/01-deployment.yaml
```

#### 1-3. DNS 해결 확인

```bash
# Prometheus Pod에서 DNS 테스트
kubectl exec -n monitoring deployment/prometheus -- \
  nslookup metrics-exporter.monitoring.svc.cluster.local

# 예상 출력:
# Address: 10.100.x.x
```

---

### 해결 방법 2: Grafana DataSource 문제

#### 2-1. DataSource 확인

Grafana UI → Configuration → Data Sources

**확인사항:**
- Name: Prometheus ✅
- Type: Prometheus ✅
- URL: http://prometheus.monitoring.svc.cluster.local:9090 ✅
- Access: Server (default) ✅

#### 2-2. DataSource 테스트

"Save & Test" 버튼 클릭

**예상 출력:**
- ✅ "Data source is working"
- ❌ "HTTP Error Bad Gateway"

**실패 시:**
```bash
# Grafana에서 Prometheus 접근 테스트
kubectl exec -n monitoring deployment/grafana -- \
  wget -qO- http://prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=up

# 예상 출력:
# {"status":"success","data":...}
```

#### 2-3. DataSource 재생성

```bash
# Grafana ConfigMap 확인
kubectl get configmap grafana-datasources -n monitoring -o yaml

# 재배포
kubectl apply -f manifests/grafana/01-grafana-config.yaml

# Grafana 재시작
kubectl rollout restart deployment/grafana -n monitoring
```

---

### 해결 방법 3: Dashboard Query 수정

Dashboard의 Query가 잘못되었을 수 있습니다.

#### 3-1. Dashboard 다시 Import

1. Grafana UI → Dashboards → Import
2. `dashboards/model-performance-dashboard.json` 선택
3. Data Source: **Prometheus** 선택 ⬅️ 중요!
4. Import

#### 3-2. Panel Query 수정

Dashboard → Panel 편집 (연필 아이콘)

**Query 예시:**
```
# Model MAE Score
model_mae_score{model_name="california-housing"}

# Model A Current MAE
model_mae_score{model_name="california-housing",version="v1.0"}

# Requests per Second
rate(model_prediction_total[1m])
```

**Legend 예시:**
```
{{version}} - {{model_name}}
```

---

## 🚀 빠른 해결 (올인원 스크립트)

```bash
#!/bin/bash
# grafana-fix.sh

echo "🔍 Step 1: Checking metrics-exporter..."
kubectl get pods -n monitoring -l app=metrics-exporter
kubectl logs -n monitoring -l app=metrics-exporter --tail=5

echo ""
echo "🔍 Step 2: Testing metrics endpoint..."
kubectl port-forward -n monitoring svc/metrics-exporter 8000:8000 &
PF_PID=$!
sleep 3
curl -s http://localhost:8000/metrics | grep model_mae_score | head -2
kill $PF_PID

echo ""
echo "🔍 Step 3: Checking Prometheus targets..."
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
PF_PID=$!
sleep 3
curl -s "http://localhost:9090/api/v1/targets" | jq '.data.activeTargets[] | select(.labels.job=="metrics-exporter") | {state, lastError}'
kill $PF_PID

echo ""
echo "🔍 Step 4: Testing Prometheus query..."
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
PF_PID=$!
sleep 3
curl -s "http://localhost:9090/api/v1/query?query=model_mae_score" | jq '.data.result[] | {metric, value}'
kill $PF_PID

echo ""
echo "✅ Diagnosis complete!"
```

---

## 📋 체크리스트

### Metrics Exporter
- [ ] Pod STATUS = Running
- [ ] RESTARTS = 0
- [ ] Logs에 "Metrics server started" 출력
- [ ] `curl localhost:8000/metrics` 응답 있음
- [ ] `model_mae_score` 메트릭 존재

### Prometheus
- [ ] targets 페이지에 `metrics-exporter` 존재
- [ ] State = UP
- [ ] Last Scrape < 30s
- [ ] Query `model_mae_score` 결과 있음

### Grafana
- [ ] DataSource "Prometheus" 존재
- [ ] DataSource Test = Success
- [ ] Dashboard Import 성공
- [ ] Data Source 선택됨
- [ ] Panel Query 정상

---

## 🎯 가장 흔한 원인 Top 5

| # | 원인 | 해결 |
|---|------|------|
| 1 | **metrics-exporter Pod 미실행** | `kubectl apply -f manifests/metrics-exporter/` |
| 2 | **Prometheus scrape 설정 없음** | ConfigMap 확인 및 재배포 |
| 3 | **Grafana DataSource 미설정** | DataSource 추가 및 테스트 |
| 4 | **Dashboard에서 DataSource 미선택** | Import 시 Prometheus 선택 |
| 5 | **Query 오타** | Panel 편집 → Query 확인 |

---

## 🔧 완전 재배포 (최후의 수단)

모든 방법이 실패했다면:

```bash
# 1. 완전 삭제
kubectl delete namespace monitoring

# 2. 재배포
export USER_NUM="01"
bash scripts/1_deploy_monitoring.sh

# 3. 포트 포워딩
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# 4. Grafana Dashboard Import
# http://localhost:3000 (admin/admin123)
# Dashboards → Import → model-performance-dashboard.json
# Data Source: Prometheus 선택!

# 5. 1-2분 대기 후 확인
```

---

## ✅ 성공 확인

**모든 것이 정상이라면:**

```
Prometheus (http://localhost:9090/targets):
✅ metrics-exporter (1/1 up)
   State: UP
   Last Scrape: 10s ago

Prometheus Query (http://localhost:9090/graph):
✅ model_mae_score
   Result: 2 series
   v1.0: 0.42
   v2.0: 0.37

Grafana Dashboard (http://localhost:3000):
✅ Model MAE Score (Real-time)
   Model A: 0.42 (빨간색 선)
   Model B: 0.37 (초록색 선)
✅ Model R² Score
   Model A: 0.85
   Model B: 0.88
✅ Requests per Second
   2.0 req/s
```

---

## 📞 여전히 "No data"라면

### 최종 진단 스크립트

```bash
# 전체 파이프라인 테스트
bash scripts/verify_setup.sh

# 또는 수동 확인:

# 1. Metrics 생성 확인
kubectl logs -n monitoring -l app=metrics-exporter | tail -20

# 2. Prometheus scrape 확인
kubectl logs -n monitoring -l app=prometheus | grep metrics-exporter

# 3. Grafana 로그 확인
kubectl logs -n monitoring -l app=grafana | grep -i error

# 4. 전체 상태 확인
kubectl get all -n monitoring
```

---

© 2024 현대오토에버 MLOps Training  
**Version**: Grafana No Data 완전 해결판  
**Status**: ✅ 단계별 진단 및 해결 가이드
