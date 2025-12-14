# Lab 3-2: Model Drift Monitoring & CI/CD Pipeline

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 90분 (Part 1: 45분 / Part 2: 45분) |
| **난이도** | ⭐⭐⭐⭐ |
| **목표** | Prometheus/Grafana 기반 모델 모니터링 및 GitHub Actions CI/CD 자동화 |
| **사전 조건** | Lab 3-1 완료, Monitoring Stack 배포됨 |

## 🎯 학습 목표

이 실습을 통해 다음을 학습합니다:

- **Prometheus 메트릭** 기반 Model Drift 감지
- **Grafana 대시보드**에서 실시간 모니터링
- **Alert Rule** 설정 및 알림 트리거
- **GitHub Actions**를 활용한 CI/CD 파이프라인 구축
- **자동 재학습 트리거** 시스템 구현
- Monitoring + CI/CD **통합 MLOps 워크플로우**

---

## 🏗️ 실습 구조

```
Lab 3-2: Monitoring & CI/CD (90분)
├── Part 1: Model Drift Monitoring (45분)
│   ├── Step 1: 기존 Monitoring Stack 확인
│   ├── Step 2: Custom Metrics 이해 및 조회
│   ├── Step 3: Drift 시뮬레이션 & 메트릭 관찰
│   ├── Step 4: Alert Rule 설정
│   └── Step 5: Grafana 대시보드 활용
└── Part 2: CI/CD Pipeline (45분)
    ├── Step 1: GitHub Actions 이해
    ├── Step 2: CI Pipeline (테스트/빌드)
    ├── Step 3: CD Pipeline (자동 배포)
    ├── Step 4: 재학습 트리거 구현
    └── Step 5: End-to-End 통합 테스트
```

---

## 📁 파일 구조

```
lab3-2_monitoring-cicd/
├── README.md                          # ⭐ 이 파일 (실습 가이드)
├── requirements.txt                   # Python 패키지
│
├── notebooks/
│   ├── lab3-2_part1_monitoring.ipynb  # Part 1: Monitoring 실습
│   └── lab3-2_part2_cicd.ipynb        # Part 2: CI/CD 실습
│
├── scripts/
│   ├── 1_check_monitoring.py          # 모니터링 스택 확인
│   ├── 2_query_metrics.py             # Prometheus 메트릭 조회
│   ├── 3_simulate_drift.py            # Drift 시뮬레이션
│   ├── 4_trigger_retrain.py           # 재학습 트리거
│   └── 5_test_cicd.sh                 # CI/CD 테스트
│
├── manifests/
│   ├── alert-rules.yaml               # Prometheus Alert Rules
│   └── drift-trigger-cronjob.yaml     # 정기 Drift 체크 CronJob
│
├── .github/workflows/
│   ├── ci-test.yaml                   # CI: 테스트 & 빌드
│   └── cd-deploy.yaml                 # CD: 자동 배포
│
├── dashboards/
│   └── drift-monitoring-dashboard.json # Drift 모니터링 대시보드
│
└── docs/
    ├── ARCHITECTURE.md                # 아키텍처 설명
    └── TROUBLESHOOTING.md             # 문제 해결
```

---

## ⚙️ 사전 준비

### 1. Monitoring Stack 확인

**이 실습은 기 구축된 Prometheus/Grafana를 활용합니다.**

```bash
# Monitoring Pod 상태 확인
kubectl get pods -n monitoring

# 예상 출력:
# NAME                            READY   STATUS    RESTARTS   AGE
# prometheus-xxx                  1/1     Running   0          1h
# grafana-xxx                     1/1     Running   0          1h
# alertmanager-xxx                1/1     Running   0          1h
```

### 2. 환경 변수 설정

```bash
# 본인의 사용자 번호로 설정
export USER_NUM="01"  # ⚠️ 본인 번호로 변경!
export NAMESPACE="kubeflow-user${USER_NUM}"

echo "사용자: user${USER_NUM}"
echo "네임스페이스: ${NAMESPACE}"
```

### 3. 포트포워딩 (터미널에서)

```bash
# Prometheus (9090)
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &

# Grafana (3000)
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# 접속 확인
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (user${USER_NUM} / mlops2025!)"
```

---

## 🚀 Part 1: Model Drift Monitoring (45분)

### 📌 학습 목표
- Prometheus에서 모델 메트릭 조회
- Drift 감지를 위한 메트릭 이해
- Alert Rule 설정 및 테스트
- Grafana 대시보드 활용

### Step 1-1: Monitoring Stack 확인

```bash
# scripts 디렉토리로 이동
cd lab3-2_monitoring-cicd

# 모니터링 스택 상태 확인
python scripts/1_check_monitoring.py
```

**예상 출력:**
```
============================================================
  Monitoring Stack Status Check
============================================================

✅ Prometheus: Running (1/1)
✅ Grafana: Running (1/1)
✅ Alertmanager: Running (1/1)
✅ Metrics Exporter (user01): Running (1/1)

📊 Prometheus Targets:
  - metrics-user01: UP
  - metrics-user02: UP
  ...

✅ 모든 컴포넌트가 정상입니다!
```

### Step 1-2: Prometheus 메트릭 조회

```bash
python scripts/2_query_metrics.py
```

**예상 출력:**
```
============================================================
  Model Metrics Query
============================================================

📊 model_mae_score (현재 MAE):
  user01: 0.3850
  user02: 0.3900
  ...

📊 model_r2_score (현재 R²):
  user01: 0.8150
  user02: 0.8100
  ...

📊 model_prediction_total (예측 횟수):
  user01: 15420 (success), 12 (error)
  ...
```

### Step 1-3: Drift 시뮬레이션

의도적으로 메트릭을 변경하여 Drift를 시뮬레이션합니다.

```bash
python scripts/3_simulate_drift.py --user user${USER_NUM} --drift-level high
```

**예상 출력:**
```
============================================================
  Drift Simulation for user01
============================================================

📉 Before Drift:
  MAE: 0.3850
  R²:  0.8150

🔄 Simulating HIGH drift...
  - Increasing MAE by 30%
  - Decreasing R² by 15%

📈 After Drift:
  MAE: 0.5005 (⚠️ 임계값 0.45 초과!)
  R²:  0.6928 (⚠️ 임계값 0.75 미만!)

🚨 Alert 조건 충족! Prometheus Alert가 발생합니다.
```

### Step 1-4: Alert Rule 확인

```bash
# Prometheus Alert Rules 확인
kubectl get configmap prometheus-config -n monitoring -o yaml | grep -A 30 "alert_rules"
```

**주요 Alert Rules:**
```yaml
- alert: HighModelMAE
  expr: model_mae_score > 0.45
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High MAE detected for {{ $labels.user_id }}"

- alert: LowModelR2
  expr: model_r2_score < 0.75
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Low R² score for {{ $labels.user_id }}"
```

### Step 1-5: Grafana 대시보드 활용

1. http://localhost:3000 접속
2. `user${USER_NUM}` / `mlops2025!` 로그인
3. **MLOps Multi-Tenant Dashboard** 선택
4. 상단 **User ID** 드롭다운에서 본인 선택
5. Drift 시뮬레이션 후 메트릭 변화 관찰

---

## 🔄 Part 2: CI/CD Pipeline (45분)

### 📌 학습 목표
- GitHub Actions 워크플로우 이해
- CI Pipeline (테스트, 빌드, 품질 검사)
- CD Pipeline (자동 배포)
- Drift 기반 자동 재학습 트리거

### Step 2-1: GitHub Actions 이해

**CI/CD 아키텍처:**
```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions CI/CD                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │   Push     │───►│   CI Job   │───►│   CD Job   │        │
│  │  to main   │    │  (Test)    │    │  (Deploy)  │        │
│  └────────────┘    └────────────┘    └────────────┘        │
│                          │                  │               │
│                          ▼                  ▼               │
│                    ┌──────────┐      ┌───────────┐         │
│                    │ Unit Test│      │ Build &   │         │
│                    │ Lint     │      │ Push ECR  │         │
│                    │ Coverage │      │ Deploy    │         │
│                    └──────────┘      │ KServe    │         │
│                                      └───────────┘         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Drift-based Auto Retrain                  │ │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐         │ │
│  │  │Prometheus│───►│  Alert   │───►│ Trigger  │         │ │
│  │  │ Metrics  │    │ Manager  │    │ Retrain  │         │ │
│  │  └──────────┘    └──────────┘    └──────────┘         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Step 2-2: CI Pipeline 분석

`.github/workflows/ci-test.yaml` 구조:

```yaml
name: CI - Test & Build

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov=src
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### Step 2-3: CD Pipeline 분석

`.github/workflows/cd-deploy.yaml` 구조:

```yaml
name: CD - Deploy to KServe

on:
  workflow_run:
    workflows: ["CI - Test & Build"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - name: Build & Push to ECR
        run: |
          docker build -t $ECR_REPO:$VERSION .
          docker push $ECR_REPO:$VERSION
      - name: Deploy to KServe
        run: |
          kubectl apply -f manifests/inferenceservice.yaml
```

### Step 2-4: 재학습 트리거 구현

Drift 감지 시 자동 재학습을 트리거합니다.

```bash
python scripts/4_trigger_retrain.py --check-drift --threshold 0.45
```

**예상 출력:**
```
============================================================
  Auto-Retrain Trigger Check
============================================================

📊 Current Metrics:
  MAE: 0.5005
  R²:  0.6928

⚠️ Drift detected! MAE > 0.45

🚀 Triggering retrain pipeline...
  - Creating GitHub workflow dispatch event
  - Pipeline: retrain-model.yaml
  - Parameters: drift_score=0.5005

✅ Retrain triggered successfully!
   Run ID: 12345678
   Monitor at: https://github.com/your-repo/actions/runs/12345678
```

### Step 2-5: End-to-End 테스트

전체 워크플로우를 테스트합니다.

```bash
./scripts/5_test_cicd.sh
```

---

## 📊 통합 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MLOps Monitoring & CI/CD                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │   Model     │────►│  Metrics    │────►│ Prometheus  │           │
│  │  Serving    │     │  Exporter   │     │   Server    │           │
│  │  (KServe)   │     │             │     │             │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                  │                   │
│                                                  ▼                   │
│                      ┌─────────────┐     ┌─────────────┐           │
│                      │   Grafana   │◄────│    Alert    │           │
│                      │  Dashboard  │     │   Manager   │           │
│                      └─────────────┘     └──────┬──────┘           │
│                                                  │                   │
│                                                  ▼                   │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │   GitHub    │◄────│   Webhook   │◄────│   Retrain   │           │
│  │   Actions   │     │   Trigger   │     │   Decision  │           │
│  └──────┬──────┘     └─────────────┘     └─────────────┘           │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  CI: Test   │────►│  CD: Build  │────►│  CD: Deploy │           │
│  │   & Lint    │     │  & Push ECR │     │  to KServe  │           │
│  └─────────────┘     └─────────────┘     └─────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✅ 완료 체크리스트

### Part 1: Monitoring
- [ ] Monitoring Stack 상태 확인 완료
- [ ] Prometheus에서 메트릭 조회 성공
- [ ] Drift 시뮬레이션 실행
- [ ] Alert 발생 확인 (Prometheus UI)
- [ ] Grafana 대시보드에서 메트릭 변화 관찰

### Part 2: CI/CD
- [ ] GitHub Actions 워크플로우 이해
- [ ] CI Pipeline 구조 분석
- [ ] CD Pipeline 구조 분석
- [ ] 재학습 트리거 테스트
- [ ] End-to-End 통합 테스트

---

## 🛠️ 문제 해결

### Prometheus 연결 실패
```bash
# 포트포워딩 확인
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Pod 상태 확인
kubectl get pods -n monitoring -l app=prometheus
```

### Grafana 로그인 실패
```bash
# 비밀번호: mlops2025!
# 계정: user01 ~ user15, user20
```

### 메트릭이 보이지 않음
```bash
# Metrics Exporter Pod 확인
kubectl get pods -n kubeflow-user${USER_NUM} -l app=metrics-exporter

# 로그 확인
kubectl logs -n kubeflow-user${USER_NUM} -l app=metrics-exporter -c exporter
```

---

## 📚 다음 단계

Lab 3-2 완료 후:
- **Lab 3-3**: Model Optimization (ONNX, 양자화)
- **프로젝트 실습**: 팀별 End-to-End MLOps 파이프라인 구축

---

© 2025 현대오토에버 MLOps Training
