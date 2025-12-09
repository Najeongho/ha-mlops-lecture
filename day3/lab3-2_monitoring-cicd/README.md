# Lab 3-2: 모니터링 시스템 구축 & CI/CD 파이프라인 통합

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 120분 (2시간) |
| **난이도** | ⭐⭐⭐⭐ |
| **목표** | Prometheus/Grafana 기반 모니터링 시스템 구축 및 A/B 테스트 피드백 기반 자동 재학습 파이프라인 구현 |

## 🎯 학습 목표

이 실습을 통해 다음을 학습합니다:
- **Prometheus**를 활용한 모델 메트릭 수집 및 모니터링
- **Grafana** 대시보드 구축 및 알림 설정
- **GitHub Actions**를 통한 CI/CD 파이프라인 자동화
- **A/B 테스트** 기반 실시간 피드백 수집
- **트리거 기반 자동 재학습** 시스템 구현
- 프로덕션 MLOps 모니터링 및 자동화 전체 워크플로우 이해

---

## 🏗️ 실습 구조

```
Lab 3-2: Monitoring & CI/CD (120분)
├── Part 1: Prometheus & Grafana 설정 (30분)
│   ├── Prometheus 배포 및 설정
│   ├── Grafana 대시보드 구축
│   └── 메트릭 수집 확인
├── Part 2: 모델 메트릭 모니터링 (30분)
│   ├── Custom Metrics Exporter 구현
│   ├── A/B 테스트 시뮬레이션
│   └── 실시간 성능 지표 수집
├── Part 3: GitHub Actions CI/CD (30분)
│   ├── GitHub Actions Workflow 구성
│   ├── 자동 테스트 및 빌드
│   └── KServe 자동 배포
└── Part 4: 트리거 기반 재학습 (30분)
    ├── 성능 저하 감지 시스템
    ├── Webhook 트리거 구성
    └── 자동 재학습 파이프라인 실행
```

---

## 📁 파일 구조

```
lab3-2_monitoring-cicd/
├── README.md                              # ⭐ 이 파일 (실습 가이드)
├── requirements.txt                       # Python 패키지
├── manifests/
│   ├── prometheus/
│   │   ├── 01-namespace.yaml             # Prometheus Namespace
│   │   ├── 02-prometheus-config.yaml     # Prometheus ConfigMap
│   │   ├── 03-prometheus-deployment.yaml # Prometheus Deployment
│   │   └── 04-prometheus-service.yaml    # Prometheus Service
│   ├── grafana/
│   │   ├── 01-grafana-config.yaml        # Grafana ConfigMap
│   │   ├── 02-grafana-deployment.yaml    # Grafana Deployment
│   │   └── 03-grafana-service.yaml       # Grafana Service
│   └── servicemonitor/
│       └── model-metrics-monitor.yaml     # ServiceMonitor for KServe
├── scripts/
│   ├── 1_deploy_monitoring.sh            # Part 1: 모니터링 스택 배포
│   ├── 2_metrics_exporter.py             # Part 2: Custom Metrics Exporter
│   ├── 3_ab_test_simulator.py            # Part 2: A/B 테스트 시뮬레이터
│   └── 4_trigger_pipeline.py             # Part 4: 재학습 트리거
├── .github/
│   └── workflows/
│       ├── ci-test.yaml                  # Part 3: CI 파이프라인
│       └── cd-deploy.yaml                # Part 3: CD 파이프라인
├── dashboards/
│   └── model-performance-dashboard.json  # Grafana 대시보드 정의
└── notebooks/
    └── monitoring_analysis.ipynb         # Jupyter 실습
```

---

## 🚀 Part 1: Prometheus & Grafana 설정 (30분)

### 학습 목표
- Prometheus로 메트릭 수집 시스템 구축
- Grafana 대시보드 설정
- 모니터링 스택 통합

### Step 1-1: 환경 변수 설정

```bash
# 사용자 네임스페이스 설정
export USER_NUM="01"  # ⚠️ 본인 번호로 변경
export USER_NAMESPACE="kubeflow-user${USER_NUM}"

echo "User Namespace: ${USER_NAMESPACE}"
```

### Step 1-2: 모니터링 스택 배포

```bash
cd lab3-2_monitoring-cicd
chmod +x scripts/*.sh

# Prometheus & Grafana 배포
./scripts/1_deploy_monitoring.sh
```

**예상 출력:**
```
============================================================
Deploying Monitoring Stack
============================================================

Step 1: Creating monitoring namespace...
✅ Namespace 'monitoring' created

Step 2: Deploying Prometheus...
✅ ConfigMap 'prometheus-config' created
✅ Deployment 'prometheus' created
✅ Service 'prometheus' created

Step 3: Deploying Grafana...
✅ ConfigMap 'grafana-datasource' created
✅ Deployment 'grafana' created
✅ Service 'grafana' created

Step 4: Waiting for pods to be ready...
✅ Prometheus is ready
✅ Grafana is ready

============================================================
Monitoring Stack Deployed Successfully!
============================================================

Access URLs:
  Prometheus: kubectl port-forward -n monitoring svc/prometheus 9090:9090
  Grafana:    kubectl port-forward -n monitoring svc/grafana 3000:3000

Default Grafana credentials:
  Username: admin
  Password: admin123
```

### Step 1-3: Prometheus UI 접속

```bash
# 포트 포워딩 (새 터미널)
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

브라우저에서 `http://localhost:9090` 접속
- Status → Targets: 수집 대상 확인
- Graph: PromQL 쿼리 테스트

### Step 1-4: Grafana UI 접속

```bash
# 포트 포워딩 (새 터미널)
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

브라우저에서 `http://localhost:3000` 접속
- **Username**: `admin`
- **Password**: `admin123`

**대시보드 임포트:**
1. 좌측 메뉴 → Dashboards → Import
2. `dashboards/model-performance-dashboard.json` 업로드
3. Data Source: `Prometheus` 선택
4. Import 클릭

---

## 📊 Part 2: 모델 메트릭 모니터링 (30분)

### 학습 목표
- Custom Metrics Exporter 구현
- A/B 테스트 시뮬레이션
- 실시간 성능 지표 수집

### Step 2-1: Metrics Exporter 배포

```bash
# Custom Metrics Exporter 실행
python scripts/2_metrics_exporter.py
```

**코드 설명:**
이 Exporter는 다음 메트릭을 수집합니다:
- `model_prediction_latency`: 예측 응답 시간
- `model_prediction_total`: 총 예측 요청 수
- `model_accuracy_score`: 실시간 정확도
- `model_mae_score`: Mean Absolute Error
- `model_version_info`: 현재 배포된 모델 버전

### Step 2-2: A/B 테스트 시뮬레이션

```bash
# A/B 테스트 트래픽 생성
python scripts/3_ab_test_simulator.py --duration 300 --requests-per-second 10
```

**예상 출력:**
```
============================================================
A/B Test Simulator
============================================================

Configuration:
  Duration: 300 seconds (5 minutes)
  Requests per second: 10
  Model A (v1.0): 50% traffic
  Model B (v2.0): 50% traffic

Starting simulation...

[00:30] Sent 300 requests
  Model A: MAE=0.42, Latency=45ms, Success=100%
  Model B: MAE=0.38, Latency=52ms, Success=100%

[01:00] Sent 600 requests
  Model A: MAE=0.43, Latency=46ms, Success=99.7%
  Model B: MAE=0.37, Latency=51ms, Success=100%

[01:30] Sent 900 requests
  Model A: MAE=0.44, Latency=47ms, Success=99.5%
  Model B: MAE=0.36, Latency=50ms, Success=100%

⚠️ Performance Alert!
  Model A MAE (0.44) exceeded threshold (0.40)
  Triggering retraining pipeline...

============================================================
Simulation Complete
============================================================

Summary:
  Total Requests: 3000
  Model A: 1500 requests, Avg MAE=0.43
  Model B: 1500 requests, Avg MAE=0.37
  Winner: Model B (13.95% improvement)
```

### Step 2-3: Grafana에서 실시간 모니터링

Grafana 대시보드로 돌아가서 확인:
1. **Model Performance** 패널
   - Model A vs Model B 성능 비교
   - MAE, Latency 트렌드
2. **Traffic Distribution** 패널
   - A/B 테스트 트래픽 분포
3. **Alert Status** 패널
   - 임계값 초과 알림

---

## 🔄 Part 3: GitHub Actions CI/CD (30분)

### 학습 목표
- GitHub Actions Workflow 구성
- 자동 테스트 및 빌드
- KServe 자동 배포

### Step 3-1: GitHub Repository 준비

```bash
# Git 초기화 (아직 안 했다면)
git init
git remote add origin https://github.com/YOUR_ORG/mlops-training-labs.git

# GitHub Secrets 설정 필요 (GitHub UI에서)
# Settings → Secrets and variables → Actions → New repository secret
```

**필요한 Secrets:**
- `AWS_ACCESS_KEY_ID`: AWS Access Key
- `AWS_SECRET_ACCESS_KEY`: AWS Secret Key
- `AWS_REGION`: `ap-northeast-2`
- `ECR_REGISTRY`: ECR 레지스트리 URL
- `KUBECONFIG_DATA`: Base64 인코딩된 kubeconfig

### Step 3-2: CI Pipeline (자동 테스트)

`.github/workflows/ci-test.yaml` 파일 확인:

```yaml
name: CI - Test Model

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: |
          pytest tests/ -v --cov=src

      - name: Run model validation
        run: |
          python scripts/validate_model.py

      - name: Check performance threshold
        run: |
          python scripts/check_threshold.py --mae-threshold 0.40
```

### Step 3-3: CD Pipeline (자동 배포)

`.github/workflows/cd-deploy.yaml` 파일 확인:

```yaml
name: CD - Deploy Model

on:
  workflow_run:
    workflows: ["CI - Test Model"]
    types: [ completed ]
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/ml-model:$IMAGE_TAG .
          docker push $ECR_REGISTRY/ml-model:$IMAGE_TAG

      - name: Deploy to KServe
        env:
          KUBECONFIG_DATA: ${{ secrets.KUBECONFIG_DATA }}
        run: |
          echo "$KUBECONFIG_DATA" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
          kubectl apply -f manifests/kserve/inference-service.yaml
```

### Step 3-4: CI/CD 테스트

```bash
# 코드 변경 및 푸시
git add .
git commit -m "feat: update model with improved features"
git push origin main

# GitHub Actions 탭에서 워크플로우 실행 확인
# https://github.com/YOUR_ORG/mlops-training-labs/actions
```

---

## 🔔 Part 4: 트리거 기반 재학습 (30분)

### 학습 목표
- 성능 저하 자동 감지
- Webhook 트리거 구성
- 자동 재학습 파이프라인 실행

### Step 4-1: 알림 규칙 설정

`manifests/prometheus/02-prometheus-config.yaml`에 알림 규칙 추가:

```yaml
groups:
  - name: model_performance
    interval: 30s
    rules:
      - alert: ModelPerformanceDegraded
        expr: model_mae_score > 0.40
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Model performance degraded"
          description: "Model MAE ({{ $value }}) exceeded threshold 0.40"

      - alert: ModelLatencyHigh
        expr: histogram_quantile(0.95, model_prediction_latency) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Model latency too high"
          description: "95th percentile latency: {{ $value }}ms"
```

### Step 4-2: Alertmanager 설정 (선택)

```bash
# Alertmanager 배포 (Slack/Email 알림)
kubectl apply -f manifests/alertmanager/
```

### Step 4-3: 재학습 트리거 스크립트

```bash
# 성능 모니터링 및 자동 트리거
python scripts/4_trigger_pipeline.py \
  --prometheus-url http://localhost:9090 \
  --mae-threshold 0.40 \
  --check-interval 60
```

**예상 출력:**
```
============================================================
Model Performance Monitor
============================================================

Configuration:
  Prometheus: http://localhost:9090
  MAE Threshold: 0.40
  Check Interval: 60 seconds

[2024-12-09 10:15:00] Checking model performance...
  Current MAE: 0.38
  Status: ✅ OK

[2024-12-09 10:16:00] Checking model performance...
  Current MAE: 0.42
  Status: ⚠️ DEGRADED (threshold: 0.40)

============================================================
Triggering Retraining Pipeline
============================================================

Step 1: Fetching recent A/B test data...
✅ Collected 5000 feedback samples

Step 2: Creating Kubeflow Pipeline Run...
✅ Pipeline created: run-2024-12-09-101600

Step 3: Monitoring pipeline execution...
  [00:30] Data preprocessing completed
  [02:15] Model training completed
  [02:45] Model evaluation completed
  [03:00] Model deployment initiated

✅ Pipeline execution completed successfully!

New Model Metrics:
  MAE: 0.36 (improved by 14.3%)
  R²: 0.87
  Version: v2.1

Deployment Status:
  InferenceService: model-serving-v2-1
  Status: Ready
  Traffic: 0% → 10% (canary)

[2024-12-09 10:19:00] Resuming monitoring...
```

### Step 4-4: Grafana 알림 설정

Grafana에서 알림 채널 구성:
1. **Alerting** → **Contact points**
2. **New contact point**
3. Type: `Slack` 또는 `Email`
4. Webhook URL 설정
5. Test 클릭

---

## 📈 전체 워크플로우 시나리오

### 시나리오: 모델 성능 저하 감지 및 자동 복구

```
1. A/B 테스트 실행
   ├─ Model A (v1.0): 기존 모델
   └─ Model B (v2.0): 신규 모델

2. Prometheus 메트릭 수집
   ├─ model_mae_score
   ├─ model_prediction_latency
   └─ model_prediction_total

3. Grafana 대시보드 모니터링
   ├─ 실시간 성능 차트
   └─ Alert 상태 확인

4. 성능 저하 감지 (MAE > 0.40)
   ├─ Alertmanager → Slack 알림
   └─ Webhook → 재학습 트리거

5. 자동 재학습 파이프라인 실행
   ├─ 최근 피드백 데이터 수집
   ├─ 모델 재학습 (Kubeflow Pipeline)
   ├─ 성능 검증 (MAE < 0.40)
   └─ KServe Canary 배포 (10% 트래픽)

6. GitHub Actions CD 파이프라인
   ├─ Docker 이미지 빌드
   ├─ ECR Push
   └─ KServe InferenceService 업데이트

7. Canary 분석 및 점진적 롤아웃
   ├─ 10% → 50% → 100% 트래픽
   └─ 성능 모니터링 지속
```

---

## 💡 핵심 개념

### 1. Prometheus 메트릭 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| **Counter** | 증가만 가능 | 총 예측 요청 수 |
| **Gauge** | 증가/감소 가능 | 현재 MAE 점수 |
| **Histogram** | 분포 측정 | 응답 시간 분포 |
| **Summary** | 백분위수 계산 | 95th percentile 지연시간 |

### 2. A/B 테스트 전략

**트래픽 분배:**
```
┌─────────────┐
│  User Traffic│
└──────┬──────┘
       │
   ┌───┴───┐
   │ 50/50 │ Split
   └───┬───┘
       │
   ┌───┴───────────┐
   │               │
┌──▼───┐      ┌───▼──┐
│Model A│      │Model B│
│ v1.0  │      │ v2.0  │
└───────┘      └───────┘
```

**메트릭 수집 및 비교:**
- Model A: Baseline (현재 프로덕션)
- Model B: Candidate (새 모델)
- 통계적 유의성 검증 (t-test)

### 3. CI/CD 파이프라인 단계

```
Code Push
    ↓
┌───────────┐
│  CI Test  │ ← Unit Test, Integration Test
└─────┬─────┘
      ↓ (Pass)
┌───────────┐
│ CD Build  │ ← Docker Build, ECR Push
└─────┬─────┘
      ↓
┌───────────┐
│ CD Deploy │ ← KServe Update, Canary
└───────────┘
```

---

## ✅ 실습 체크리스트

### Part 1: Prometheus & Grafana
- [ ] Prometheus 배포 완료
- [ ] Grafana 배포 완료
- [ ] Prometheus UI 접속 확인 (localhost:9090)
- [ ] Grafana UI 접속 확인 (localhost:3000)
- [ ] 대시보드 임포트 완료

### Part 2: 모델 메트릭 모니터링
- [ ] Metrics Exporter 실행
- [ ] A/B 테스트 시뮬레이션 완료
- [ ] Grafana에서 실시간 메트릭 확인
- [ ] 알림 규칙 동작 확인

### Part 3: GitHub Actions CI/CD
- [ ] GitHub Repository 설정
- [ ] Secrets 구성 완료
- [ ] CI Pipeline 실행 성공
- [ ] CD Pipeline 실행 성공

### Part 4: 트리거 기반 재학습
- [ ] 성능 모니터링 스크립트 실행
- [ ] 임계값 초과 시 자동 트리거 확인
- [ ] 재학습 파이프라인 실행 성공
- [ ] 새 모델 배포 확인

---

## 📊 성과 지표

실습 완료 후 다음을 확인할 수 있습니다:

| 지표 | 목표 | 실제 |
|------|------|------|
| 모델 성능 (MAE) | < 0.40 | _____ |
| 예측 지연시간 (P95) | < 100ms | _____ |
| CI/CD 파이프라인 시간 | < 10분 | _____ |
| 재학습 트리거 → 배포 | < 20분 | _____ |
| 성능 개선률 | > 10% | _____ |

---

## ❓ 트러블슈팅

### 문제 1: Prometheus가 메트릭을 수집하지 못함

**원인:** ServiceMonitor 설정 오류

**해결:**
```bash
# ServiceMonitor 확인
kubectl get servicemonitor -n monitoring

# Prometheus 타겟 확인
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# 브라우저: http://localhost:9090/targets
```

### 문제 2: Grafana 대시보드가 데이터를 표시하지 않음

**원인:** Prometheus Data Source 미연결

**해결:**
1. Grafana → Configuration → Data Sources
2. Prometheus 추가
3. URL: `http://prometheus.monitoring.svc.cluster.local:9090`
4. Save & Test

### 문제 3: GitHub Actions가 실패함

**원인:** Secrets 미설정 또는 권한 부족

**해결:**
```bash
# Secrets 확인
# GitHub Repository → Settings → Secrets and variables → Actions

# KUBECONFIG 생성
kubectl config view --flatten --minify > kubeconfig.yaml
base64 -w 0 kubeconfig.yaml > kubeconfig.base64
# 이 내용을 KUBECONFIG_DATA Secret에 추가
```

### 문제 4: 재학습 트리거가 동작하지 않음

**원인:** Prometheus 쿼리 오류 또는 권한 문제

**해결:**
```bash
# Prometheus 쿼리 테스트
curl http://localhost:9090/api/v1/query?query=model_mae_score

# RBAC 권한 확인
kubectl auth can-i create pipelineruns -n ${USER_NAMESPACE}
```

---

## 🔗 참고 자료

### Prometheus
- [Prometheus 공식 문서](https://prometheus.io/docs/)
- [PromQL 쿼리 가이드](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)

### Grafana
- [Grafana 공식 문서](https://grafana.com/docs/)
- [대시보드 생성 가이드](https://grafana.com/docs/grafana/latest/dashboards/)
- [Alert 설정](https://grafana.com/docs/grafana/latest/alerting/)

### GitHub Actions
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Workflow 구문](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [AWS 배포 예제](https://github.com/aws-actions)

### A/B Testing
- [A/B Testing 모범 사례](https://www.optimizely.com/optimization-glossary/ab-testing/)
- [Statistical Significance](https://www.evanmiller.org/ab-testing/)

---

## 📝 실습 노트

### 성능 비교 결과

| 모델 | MAE | Latency | Accuracy |
|------|-----|---------|----------|
| Model A (v1.0) | _____ | _____ | _____ |
| Model B (v2.0) | _____ | _____ | _____ |
| 개선률 | _____ | _____ | _____ |

### 학습 내용 정리

**가장 인상 깊었던 부분:**
- 

**어려웠던 부분:**
- 

**실무 적용 아이디어:**
- 

---

## 🎯 다음 단계

1. **고급 모니터링:**
   - Jaeger로 분산 추적 구현
   - ELK Stack으로 로그 수집

2. **고급 배포 전략:**
   - Blue-Green 배포
   - Feature Flag 기반 배포

3. **MLOps 플랫폼 확장:**
   - Multi-cluster 배포
   - GitOps (Argo CD) 도입

---

© 2024 현대오토에버 MLOps Training - Lab 3-2
