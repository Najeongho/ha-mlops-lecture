# Lab 2-1: FastAPI 모델 서빙

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 50분 |
| **난이도** | ⭐⭐ |
| **목표** | FastAPI로 ML 모델 REST API 구축 및 Kubernetes 배포 |

## 🎯 학습 목표

- Scikit-learn 모델 학습 및 저장
- FastAPI로 추론 API 구현
- **로컬 환경에서 API 테스트**
- Docker 이미지 빌드 (멀티 플랫폼 지원)
- Kubernetes Deployment/Service 배포

## 🏗️ 아키텍처

```
┌──────────────────────────────────────────────────────────┐
│  Local Development                                        │
│  ┌──────────────┐    ┌─────────────────────────────────┐│
│  │ train_model  │───▶│ model.joblib                    ││
│  │     .py      │    └─────────────────────────────────┘│
│  └──────────────┘                                        │
│         │                                                 │
│         ▼                                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  FastAPI App (uvicorn)                           │   │
│  │  http://localhost:8000                           │   │
│  │  - GET  /health                                  │   │
│  │  - GET  /docs (Swagger UI)                       │   │
│  │  - POST /predict                                 │   │
│  │  - POST /predict/batch                           │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                       │
                       │ docker build
                       ▼
┌──────────────────────────────────────────────────────────┐
│  Production (Kubernetes on EKS)                          │
│  ┌─────────┐     ┌───────────────┐                      │
│  │ Service │────▶│  Deployment   │                      │
│  │  :80    │     │  ┌─────────┐  │                      │
│  └─────────┘     │  │ Pod 1   │  │                      │
│                  │  │ FastAPI │  │                      │
│                  │  └─────────┘  │                      │
│                  │  ┌─────────┐  │                      │
│                  │  │ Pod 2   │  │                      │
│                  │  └─────────┘  │                      │
│                  └───────────────┘                      │
└──────────────────────────────────────────────────────────┘
```

## 📁 파일 구조

```
lab2-1_fastapi-serving/
├── README.md                    # 이 파일
├── CHANGELOG.md                 # 수정 내역
├── .gitignore                   # Git 제외 파일
│
├── train_model.py               # 모델 학습 스크립트
├── requirements.txt             # Python 의존성
│
├── app/                         # FastAPI 애플리케이션
│   ├── __init__.py
│   └── main.py                  # API 구현
│
├── Dockerfile                   # Docker 이미지 빌드
├── deployment.yaml              # Kubernetes Deployment
├── service.yaml                 # Kubernetes Service
│
├── scripts/                     # 유틸리티 스크립트
│   ├── local_test.sh            # 로컬 테스트
│   └── build_and_deploy.sh      # 빌드 및 배포
│
└── tests/                       # 테스트 파일
    └── test_api.sh              # API 통합 테스트
```

## 🚀 실습 가이드

### Phase 1: 로컬 개발 및 테스트

#### Step 1-1: 가상환경 설정 (권장)

```bash
# Python 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

#### Step 1-2: 모델 학습

```bash
python train_model.py
```

**예상 출력:**
```
============================================================
  Training Iris Classification Model
============================================================

[1/4] Loading Iris dataset...
  - Samples: 150
  - Features: 4
  - Classes: ['setosa', 'versicolor', 'virginica']

[2/4] Splitting data...
  - Train samples: 120
  - Test samples: 30

[3/4] Training RandomForest model...
  - Accuracy: 1.0000

  Classification Report:
              precision    recall  f1-score   support
      setosa       1.00      1.00      1.00        10
  versicolor       1.00      1.00      1.00         9
   virginica       1.00      1.00      1.00        11

[4/4] Saving model...
  ✅ Model saved: model.joblib
```

#### Step 1-3: FastAPI 앱 로컬 실행

```bash
# 방법 1: uvicorn 직접 실행 (개발 모드)
uvicorn app.main:app --reload --port 8000

# 방법 2: Python으로 실행
python -m app.main

# 방법 3: 스크립트 사용
chmod +x scripts/local_test.sh
./scripts/local_test.sh
```

**예상 출력:**
```
✅ Model loaded successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Step 1-4: API 테스트

**터미널 1: API 서버 실행 상태 유지**

**터미널 2: API 테스트**

```bash
# 1. Health Check
curl http://localhost:8000/health

# 예상 응답:
# {
#   "status": "healthy",
#   "model_loaded": true
# }

# 2. Swagger UI 접속
# 브라우저에서: http://localhost:8000/docs

# 3. 단일 예측 (Setosa)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'

# 예상 응답:
# {
#   "prediction": 0,
#   "class_name": "setosa",
#   "probability": 0.97,
#   "probabilities": [0.97, 0.02, 0.01]
# }

# 4. 배치 예측
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
    {"sepal_length": 6.0, "sepal_width": 2.7, "petal_length": 4.2, "petal_width": 1.3}
  ]'

# 5. 통합 테스트 스크립트 실행
chmod +x tests/test_api.sh
API_URL=http://localhost:8000 ./tests/test_api.sh
```

#### Step 1-5: 로컬 테스트 체크리스트

- [ ] `model.joblib` 파일 생성 확인
- [ ] 가상환경 활성화 및 의존성 설치
- [ ] FastAPI 서버가 8000 포트에서 실행 중
- [ ] Health check 엔드포인트 응답 (200 OK)
- [ ] Swagger UI 접속 가능 (`http://localhost:8000/docs`)
- [ ] Predict 엔드포인트 정상 동작
- [ ] 배치 예측 엔드포인트 정상 동작

---

### Phase 2: Docker 빌드 및 로컬 테스트

#### Step 2-1: Docker 이미지 빌드

```bash
# AMD64 플랫폼으로 빌드 (EKS 호환)
docker build --platform linux/amd64 -t iris-api:v1 .

# 빌드 확인
docker images | grep iris-api
```

#### Step 2-2: Docker 컨테이너 로컬 테스트

```bash
# 컨테이너 실행
docker run -d -p 8000:8000 --name iris-api-test iris-api:v1

# 로그 확인
docker logs iris-api-test

# API 테스트
curl http://localhost:8000/health
API_URL=http://localhost:8000 ./tests/test_api.sh

# 컨테이너 중지 및 삭제
docker stop iris-api-test
docker rm iris-api-test
```

---

### Phase 3: Kubernetes 배포

#### Step 3-1: 환경 변수 설정

```bash
# ECR 레지스트리 (AWS Console에서 확인)
export ECR_REGISTRY="<AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com"

# 본인의 Namespace (수강생 번호에 맞게 변경)
export NAMESPACE="kubeflow-user00"

# 확인
echo $ECR_REGISTRY
echo $NAMESPACE
```

#### Step 3-2: ECR에 이미지 푸시

```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# 이미지 태그 및 푸시
docker tag iris-api:v1 $ECR_REGISTRY/mlops-training/iris-api:v1
docker push $ECR_REGISTRY/mlops-training/iris-api:v1

# ECR 이미지 확인
aws ecr describe-images \
  --repository-name mlops-training/iris-api \
  --image-ids imageTag=v1 \
  --region ap-northeast-2
```

#### Step 3-3: Kubernetes 리소스 배포

```bash
# Manifest 파일 변수 치환
envsubst < deployment.yaml > deployment-ready.yaml
envsubst < service.yaml > service-ready.yaml

# 배포
kubectl apply -f deployment-ready.yaml
kubectl apply -f service-ready.yaml

# 상태 확인
kubectl get pods -n $NAMESPACE -l app=iris-api
kubectl get svc -n $NAMESPACE iris-api-svc
kubectl get hpa -n $NAMESPACE iris-api-hpa
```

#### Step 3-4: Kubernetes API 테스트

```bash
# 포트 포워딩
kubectl port-forward svc/iris-api-svc 8080:80 -n $NAMESPACE

# 다른 터미널에서 테스트
curl http://localhost:8080/health
API_URL=http://localhost:8080 ./tests/test_api.sh
```

#### Step 3-5: 자동화 스크립트 사용 (권장)

```bash
# 전체 빌드 및 배포 자동화
chmod +x scripts/build_and_deploy.sh

# 환경 변수 설정 후 실행
export ECR_REGISTRY="<AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com"
export NAMESPACE="kubeflow-user00"

./scripts/build_and_deploy.sh
```

---

## 📊 API 명세

### 1. Health Check
- **URL:** `GET /health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "model_loaded": true
  }
  ```

### 2. 단일 예측
- **URL:** `POST /predict`
- **Request Body:**
  ```json
  {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }
  ```
- **Response:**
  ```json
  {
    "prediction": 0,
    "class_name": "setosa",
    "probability": 0.97,
    "probabilities": [0.97, 0.02, 0.01]
  }
  ```

### 3. 배치 예측
- **URL:** `POST /predict/batch`
- **Request Body:**
  ```json
  [
    {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
    {"sepal_length": 6.0, "sepal_width": 2.7, "petal_length": 4.2, "petal_width": 1.3}
  ]
  ```

### 4. Swagger UI
- **URL:** `GET /docs`
- 대화형 API 문서 및 테스트 인터페이스

---

## ❓ 트러블슈팅

### 로컬 실행 문제

#### 문제: `ModuleNotFoundError`
```bash
# 해결: 가상환경 확인 및 의존성 재설치
pip install -r requirements.txt
```

#### 문제: `model.joblib` 파일 없음
```bash
# 해결: 모델 학습 실행
python train_model.py
```

#### 문제: 포트 8000이 이미 사용 중
```bash
# 해결: 다른 포트 사용
uvicorn app.main:app --reload --port 8001

# 또는 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9  # macOS/Linux
# netstat -ano | findstr :8000  # Windows
```

### Docker 빌드 문제

#### 문제: `exec format error` (CrashLoopBackOff)
```bash
# 원인: 아키텍처 불일치 (ARM64 vs AMD64)
# 해결: --platform 플래그 사용
docker build --platform linux/amd64 -t iris-api:v1 .
```

#### 문제: Docker 빌드 느림
```bash
# 해결: BuildKit 활성화
export DOCKER_BUILDKIT=1
docker build --platform linux/amd64 -t iris-api:v1 .
```

### Kubernetes 배포 문제

#### 문제: `ImagePullBackOff`
```bash
# 원인 1: ECR 로그인 만료
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# 원인 2: 이미지 경로 오류
kubectl describe pod <pod-name> -n $NAMESPACE
# Events 섹션에서 정확한 에러 확인

# 원인 3: IAM 권한 부족
aws iam get-role --role-name <node-role-name>
```

#### 문제: `CrashLoopBackOff`
```bash
# 로그 확인
kubectl logs <pod-name> -n $NAMESPACE

# 일반적인 원인:
# 1. model.joblib 파일 누락 → Docker 이미지 재빌드
# 2. 아키텍처 불일치 → --platform linux/amd64로 재빌드
# 3. 메모리 부족 → deployment.yaml의 resources.limits 증가
```

#### 문제: HPA가 메트릭을 수집하지 못함
```bash
# Metrics Server 확인
kubectl get deployment metrics-server -n kube-system

# HPA 상세 정보
kubectl describe hpa iris-api-hpa -n $NAMESPACE
```

---

## 🧪 테스트 전략

### 1. 단위 테스트 (로컬)
```bash
# FastAPI 서버 실행
uvicorn app.main:app --reload

# 각 엔드포인트 개별 테스트
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{...}'
```

### 2. 통합 테스트 (로컬)
```bash
# 전체 테스트 스크립트 실행
./tests/test_api.sh
```

### 3. Docker 컨테이너 테스트
```bash
docker run -d -p 8000:8000 iris-api:v1
./tests/test_api.sh
```

### 4. Kubernetes 환경 테스트
```bash
kubectl port-forward svc/iris-api-svc 8080:80 -n $NAMESPACE
API_URL=http://localhost:8080 ./tests/test_api.sh
```

---

## 📚 주요 개념

### FastAPI 장점
- **빠른 개발**: Python 타입 힌트 기반 자동 검증
- **자동 문서화**: Swagger UI 자동 생성
- **높은 성능**: ASGI 기반 비동기 처리
- **검증**: Pydantic 모델로 입력/출력 검증

### Docker 멀티 플랫폼
- **ARM64**: Apple Silicon (M1/M2) 맥북
- **AMD64**: 대부분의 클라우드 환경 (AWS, GCP, Azure)
- **해결책**: `--platform linux/amd64` 플래그 사용

### Kubernetes의 주요 리소스
- **Deployment**: Pod 복제 및 롤링 업데이트 관리
- **Service**: Pod에 안정적인 네트워크 엔드포인트 제공
- **HPA**: CPU/메모리 사용량에 따라 자동 스케일링

---

## ✅ 완료 체크리스트

### 로컬 개발
- [ ] Python 가상환경 생성 및 활성화
- [ ] `model.joblib` 파일 생성
- [ ] FastAPI 서버 로컬 실행 성공
- [ ] Swagger UI 접속 확인
- [ ] 모든 API 엔드포인트 테스트 통과

### Docker
- [ ] Docker 이미지 빌드 (AMD64 플랫폼)
- [ ] 로컬에서 Docker 컨테이너 실행 테스트
- [ ] ECR 로그인 성공
- [ ] ECR에 이미지 푸시 완료

### Kubernetes
- [ ] Deployment 생성 (2 replicas)
- [ ] Service 생성 (ClusterIP)
- [ ] HPA 설정 완료
- [ ] 모든 Pod가 Running 상태
- [ ] Kubernetes 환경에서 API 테스트 통과

---

## 🎓 학습 포인트

1. **로컬 개발의 중요성**
   - 빠른 반복: Docker 빌드 없이 즉시 테스트
   - 디버깅 용이: 에러 메시지 즉시 확인
   - 비용 절감: 클라우드 리소스 사용 전 검증

2. **FastAPI 베스트 프랙티스**
   - Pydantic 모델로 입력/출력 검증
   - Type hints로 자동 문서화
   - Health check 엔드포인트 필수

3. **Docker 아키텍처 고려**
   - 개발 환경과 프로덕션 환경의 아키텍처 차이
   - `--platform` 플래그로 명시적 지정
   - 멀티 플랫폼 빌드의 중요성

4. **Kubernetes 리소스 관리**
   - Deployment로 선언적 배포
   - Service로 안정적인 네트워크 제공
   - HPA로 자동 스케일링

---

## 📞 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Docker 멀티 플랫폼 빌드](https://docs.docker.com/build/building/multi-platform/)
- [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [HPA 가이드](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

---

## 📝 수정 내역

상세한 수정 내역은 [CHANGELOG.md](./CHANGELOG.md)를 참조하세요.

---

**🎉 Lab 2-1을 완료하셨습니다!**

다음 단계: [Lab 2-2: MLflow Tracking & Registry](../lab2-2_mlflow-tracking/)
