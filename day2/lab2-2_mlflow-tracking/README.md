# Lab 2-2: MLflow Tracking 완전 가이드

## 📚 파일 구조 및 사용법

Lab 2-2는 여러 방식으로 실습할 수 있도록 구성되어 있습니다.

```
lab2-2_mlflow-tracking/
├── mlflow_experiment.ipynb         # ⭐ 메인 실습 노트북 (Jupyter)
├── mlflow_experiment.py            # CLI 실행 스크립트
├── mlflow_config.py                # MLflow 설정 파일
├── compare_experiments.py          # 실험 비교 스크립트
├── model_registry.py               # Model Registry 관리
└── README.md                       # 문서
```

---

## 🎯 실습 방법

### ✅ 방법 1: Jupyter Notebook (권장)

**Kubeflow Notebook에서 실행:**

1. **완전한 노트북 다운로드**:
   - [mlflow_experiment_complete.ipynb](computer:///mnt/user-data/outputs/mlflow_experiment_complete.ipynb)

2. **Notebook 업로드**:
   - Kubeflow Jupyter Lab에서 Upload 버튼 클릭
   - 다운로드한 파일 선택

3. **셀 순서대로 실행** (Shift + Enter):
   ```
   Cell 1: 패키지 설치
   Cell 2: Import 문
   Cell 3: MLflow 설정
   Cell 4: 데이터 로드
   Cell 5: 실험 생성
   Cell 6: 첫 번째 Run
   ... (순서대로 계속)
   ```

4. **⚠️ 중요**: 
   - 반드시 **순서대로** 실행하세요
   - 중간 셀을 건너뛰면 NameError 발생
   - 에러 발생 시 Cell 1부터 다시 실행

---

### ✅ 방법 2: Python 스크립트 (CLI)

터미널에서 실행:

```bash
# 1. 환경 변수 설정
export MLFLOW_TRACKING_URI="http://mlflow-server-service.mlflow-system.svc.cluster.local:5000"
export MLFLOW_S3_ENDPOINT_URL="http://minio-service.kubeflow.svc:9000"
export AWS_ACCESS_KEY_ID="minio"
export AWS_SECRET_ACCESS_KEY="minio123"

# 2. 메인 실험 실행
python mlflow_experiment.py

# 3. 실험 비교 (선택)
python compare_experiments.py --experiment california-housing

# 4. Model Registry 관리 (선택)
python model_registry.py
```

---

## 📁 각 파일 설명

### 1️⃣ mlflow_experiment.ipynb (⭐ 메인 실습)

**용도**: Jupyter Notebook 실습용

**내용**:
- MLflow 기본 사용법
- 파라미터/메트릭 로깅
- 여러 모델 비교
- Model Registry 사용
- 시각화

**실행**: Jupyter Lab에서 순서대로 실행

---

### 2️⃣ mlflow_experiment.py

**용도**: 독립 실행 Python 스크립트

**내용**:
- mlflow_experiment.ipynb의 CLI 버전
- 3개의 RandomForest 모델 실험
- 결과 비교 출력

**실행**:
```bash
python mlflow_experiment.py
```

**출력 예시**:
```
============================================================
  Lab 2-2: MLflow Experiment Tracking
============================================================

[Setup] Experiment: california-housing
[1/5] Loading California Housing dataset...
  - Training samples: 16512
  - Test samples: 4128

[Run] rf-small
  Parameters: n_estimators=50, max_depth=5
[Run] rf-medium
  Parameters: n_estimators=100, max_depth=10
[Run] rf-large
  Parameters: n_estimators=200, max_depth=15

============================================================
  Experiment Results Summary
============================================================

  Run Name        R2 Score  
  -------------------------
  rf-large        0.8123    ← Best
  rf-medium       0.8056
  rf-small        0.7834

✅ All experiments completed!
💡 View results at MLflow UI: http://localhost:5000
```

---

### 3️⃣ compare_experiments.py

**용도**: 실험 결과 비교 및 시각화

**실행**:
```bash
python compare_experiments.py --experiment california-housing-lab
```

**기능**:
- 실험의 모든 Run 조회
- 메트릭 비교 테이블 생성
- 시각화 그래프 저장

---

### 4️⃣ model_registry.py

**용도**: Model Registry 관리

**실행**:
```bash
python model_registry.py
```

**기능**:
- 최고 성능 모델 자동 찾기
- Model Registry 등록
- Production 스테이지 전환
- 모델 버전 관리

---

### 5️⃣ mlflow_config.py

**용도**: MLflow 설정 유틸리티

**내용**:
```python
def configure_mlflow():
    """MLflow 환경 변수 설정"""
    tracking_uri = os.getenv(
        'MLFLOW_TRACKING_URI',
        'http://mlflow-server-service.mlflow-system.svc.cluster.local:5000'
    )
    mlflow.set_tracking_uri(tracking_uri)
    # S3/MinIO 설정...
```

**사용**: 다른 스크립트에서 import

---

## ⚠️ 일반적인 에러 해결

### ❌ NameError: name 'RandomForestRegressor' is not defined

**원인**: Import 문이 실행되지 않음

**해결**:
```python
# 반드시 먼저 실행!
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
```

---

### ❌ NameError: name 'pd' is not defined

**원인**: Pandas import 누락

**해결**:
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

---

### ❌ NameError: name 'results_df' is not defined

**원인**: 이전 셀이 실행되지 않음

**해결**: 
- Cell 1부터 순서대로 다시 실행
- "Kernel → Restart & Run All" 클릭

---

### ❌ ModuleNotFoundError: No module named 'mlflow'

**원인**: 패키지 미설치

**해결**:
```bash
!pip install mlflow==2.9.2 boto3 scikit-learn pandas matplotlib
```

---

### ❌ Distutils Warning

**원인**: Python 패키지 시스템 경고 (무해)

**해결**: 무시해도 됨. 실행에는 영향 없음

---

## 🎓 실습 흐름

### Step 1: 환경 설정
```python
# 1. 패키지 설치
!pip install mlflow==2.9.2 boto3 scikit-learn pandas matplotlib

# 2. Import
import mlflow, pandas, numpy, sklearn...

# 3. MLflow 설정
mlflow.set_tracking_uri(...)
```

### Step 2: 데이터 준비
```python
# California Housing 데이터 로드
data = fetch_california_housing()
X_train, X_test, y_train, y_test = train_test_split(...)
```

### Step 3: 첫 번째 실험
```python
with mlflow.start_run(run_name="rf-baseline"):
    mlflow.log_params({...})
    model.fit(X_train, y_train)
    mlflow.log_metrics({...})
    mlflow.sklearn.log_model(model, "model")
```

### Step 4: 여러 실험
```python
experiments = [
    (RandomForestRegressor, {...}, "rf-small"),
    (GradientBoostingRegressor, {...}, "gb-baseline"),
    ...
]
for model_class, params, name in experiments:
    run_experiment(model_class, params, name)
```

### Step 5: 결과 비교
```python
results_df = pd.DataFrame(results)
results_df.sort_values('r2', ascending=False)
```

### Step 6: 시각화
```python
plt.barh(results_df['name'], results_df['r2'])
plt.show()
```

### Step 7: Model Registry
```python
mlflow.register_model(model_uri, "california-housing-model")
```

---

## 📊 MLflow UI 사용법

### 1. 접속

```bash
# 터미널에서 포트 포워딩
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
```

브라우저: http://localhost:5000

### 2. 실험 선택

- 왼쪽 사이드바에서 `california-housing-lab` 클릭

### 3. Run 비교

1. 여러 Run 체크박스 선택
2. **Compare** 버튼 클릭
3. 파라미터/메트릭 비교 확인

### 4. 모델 다운로드

1. Run 상세 페이지
2. **Artifacts** 탭
3. `model/` 폴더 → **Download** 버튼

---

## 🔗 관련 파일

- **MLflow 배포 가이드**: [MLflow-Deployment-Guide.md](computer:///mnt/user-data/outputs/MLflow-Deployment-Guide.md)
- **완전한 실습 노트북**: [mlflow_experiment_complete.ipynb](computer:///mnt/user-data/outputs/mlflow_experiment_complete.ipynb)

---

## ✅ 체크리스트

- [ ] MLflow 서버 정상 실행 확인
- [ ] 포트 포워딩 설정
- [ ] Notebook 업로드
- [ ] Cell 1-3 실행 (환경 설정)
- [ ] Cell 4-5 실행 (데이터 준비)
- [ ] Cell 6 실행 (첫 실험)
- [ ] Cell 7-9 실행 (여러 실험)
- [ ] Cell 10-11 실행 (비교/시각화)
- [ ] Cell 12 실행 (Model Registry)
- [ ] MLflow UI 접속 확인

---

## 🎯 학습 목표 달성 확인

✅ MLflow Tracking 기본 개념 이해  
✅ 파라미터, 메트릭, 아티팩트 로깅  
✅ 여러 실험 비교  
✅ Model Registry 사용  
✅ MLflow UI 활용  

**모두 완료하면 Lab 2-3으로 진행!** 🎉
