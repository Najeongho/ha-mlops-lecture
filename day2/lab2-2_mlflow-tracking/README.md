# Lab 2-2: MLflow Tracking & Model Registry

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 60분 |
| **난이도** | ⭐⭐ |
| **목표** | MLflow로 실험 추적 및 모델 버전 관리 |

## 🎯 학습 목표

- MLflow Tracking으로 실험 기록
- 파라미터, 메트릭, 아티팩트 로깅
- MLflow Model Registry 사용
- 모델 스테이지 관리 (Staging → Production)

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     MLflow Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌─────────────────┐     ┌─────────────┐  │
│  │  Client  │────▶│  Tracking API   │────▶│  Backend    │  │
│  │(Notebook)│     │                 │     │  Store      │  │
│  └──────────┘     └─────────────────┘     │ (PostgreSQL)│  │
│                           │               └─────────────┘  │
│                           │                                │
│                           ▼                                │
│                   ┌─────────────────┐                      │
│                   │ Artifact Store  │                      │
│                   │    (S3/MinIO)   │                      │
│                   └─────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 파일 구조

```
lab2-2_mlflow-tracking/
├── README.md
├── mlflow_experiment.py          # 실험 추적 코드
├── mlflow_experiment.ipynb       # Jupyter Notebook
├── model_registry.py             # Model Registry 코드
├── mlflow_config.py              # MLflow 설정
└── compare_experiments.py        # 실험 비교 스크립트
```

## 🔧 실습 단계

### Step 1: MLflow 서버 접속 확인

```bash
# 포트 포워딩
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000

# 브라우저에서 접속
http://localhost:5000
```

### Step 2: 환경 변수 설정

```python
import os

os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow-server-service.mlflow-system.svc.cluster.local:5000'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://minio-service.kubeflow.svc:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'
```

### Step 3: 실험 추적 실행

```bash
python mlflow_experiment.py
```

### Step 4: MLflow UI에서 확인

1. 브라우저에서 `http://localhost:5000` 접속
2. 실험 목록에서 `california-housing` 선택
3. 각 Run 클릭하여 파라미터/메트릭 확인
4. 여러 Run 선택 후 Compare 클릭

### Step 5: Model Registry 사용

```bash
python model_registry.py
```

## ✅ 완료 체크리스트

- [ ] MLflow 서버 접속 성공
- [ ] 실험 생성 및 Run 기록
- [ ] 파라미터/메트릭 로깅
- [ ] 모델 아티팩트 저장
- [ ] Model Registry 등록
- [ ] Production 스테이지 전환

## 📊 MLflow 핵심 개념

### Tracking 구조

```
Experiment (california-housing)
├── Run 1 (rf-baseline)
│   ├── Parameters: n_estimators=50, max_depth=5
│   ├── Metrics: r2=0.78, mse=0.35
│   └── Artifacts: model/, plots/
├── Run 2 (rf-tuned)
│   ├── Parameters: n_estimators=100, max_depth=10
│   ├── Metrics: r2=0.85, mse=0.19
│   └── Artifacts: model/, plots/
└── Run 3 (rf-optimized)
    └── ...
```

### Model Registry 스테이지

| Stage | 설명 |
|-------|------|
| None | 초기 상태 |
| Staging | 테스트/검증 중 |
| Production | 운영 배포 |
| Archived | 보관 (이전 버전) |

## ❓ 트러블슈팅

### 문제: "MLFLOW_TRACKING_URI not set"

```python
import mlflow
mlflow.set_tracking_uri("http://mlflow-server-service.mlflow-system.svc.cluster.local:5000")
```

### 문제: S3 연결 오류

```python
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://minio-service.kubeflow.svc:9000'
os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'
```

## 📚 참고 자료

- [MLflow 공식 문서](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
