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
- Docker 이미지 빌드
- Kubernetes Deployment/Service 배포

## 🏗️ 아키텍처

```
┌──────────┐     ┌─────────────────────────────────────┐
│  Client  │────▶│  Kubernetes                         │
│  (curl)  │     │  ┌─────────┐     ┌───────────────┐ │
└──────────┘     │  │ Service │────▶│  Deployment   │ │
                 │  │  :80    │     │  ┌─────────┐  │ │
                 │  └─────────┘     │  │ Pod 1   │  │ │
                 │                  │  │ FastAPI │  │ │
                 │                  │  │ + Model │  │ │
                 │                  │  └─────────┘  │ │
                 │                  │  ┌─────────┐  │ │
                 │                  │  │ Pod 2   │  │ │
                 │                  │  └─────────┘  │ │
                 │                  └───────────────┘ │
                 └─────────────────────────────────────┘
```

## 📁 파일 구조

```
lab2-1_fastapi-serving/
├── README.md
├── train_model.py           # 모델 학습 스크립트
├── app/
│   └── main.py              # FastAPI 애플리케이션
├── Dockerfile               # Docker 이미지 빌드
├── requirements.txt         # Python 의존성
├── deployment.yaml          # Kubernetes Deployment
├── service.yaml             # Kubernetes Service
└── test_api.sh              # API 테스트 스크립트
```

## 🔧 실습 단계

### Step 1: 모델 학습 및 저장

```bash
python train_model.py
```

### Step 2: FastAPI 앱 테스트 (로컬)

```bash
# 의존성 설치
pip install -r requirements.txt

# 로컬 실행
uvicorn app.main:app --reload --port 8000

# 테스트 (다른 터미널)
curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

### Step 3: Docker 빌드 및 푸시

```bash
# 빌드
docker build -t iris-api:v1 .

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}

# 태그 및 푸시
docker tag iris-api:v1 ${ECR_REGISTRY}/mlops-training/iris-api:v1
docker push ${ECR_REGISTRY}/mlops-training/iris-api:v1
```

### Step 4: Kubernetes 배포

```bash
# namespace 변수 업데이트 후
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 상태 확인
kubectl get pods -n kubeflow-userXX
kubectl get svc -n kubeflow-userXX
```

### Step 5: API 테스트

```bash
# 포트 포워딩
kubectl port-forward svc/iris-api-svc 8080:80 -n kubeflow-userXX

# API 호출
./test_api.sh
```

## ✅ 완료 체크리스트

- [ ] 모델 학습 및 저장 (model.joblib)
- [ ] FastAPI 앱 로컬 테스트
- [ ] Docker 이미지 빌드 및 ECR 푸시
- [ ] Kubernetes Deployment 생성
- [ ] Service를 통한 API 호출 성공

## 📊 API 명세

### POST /predict

**Request:**
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

**Response:**
```json
{
  "prediction": 0,
  "class_name": "setosa",
  "probability": 0.97
}
```

### GET /health

**Response:**
```json
{
  "status": "healthy"
}
```

## ❓ 트러블슈팅

### 문제: ImagePullBackOff

```bash
kubectl describe pod [pod-name] -n kubeflow-userXX
# ECR 이미지 경로 확인
# ECR 로그인 확인
```

### 문제: CrashLoopBackOff

```bash
kubectl logs [pod-name] -n kubeflow-userXX
# 애플리케이션 에러 확인
```
