# Lab 2-1: FastAPI 모델 서빙

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 50분 |
| **난이도** | ⭐⭐ |
| **목표** | FastAPI로 ML 모델 REST API 구축 |

## 🎯 학습 목표

- Scikit-learn 모델 학습
- FastAPI로 추론 API 구현
- Docker 이미지 빌드
- Kubernetes 배포

## 🚀 실습 단계

### Step 1: 로컬 개발

```bash
# 모델 학습
python train_model.py

# FastAPI 서버 실행
uvicorn app.main:app --reload --port 8000

# API 테스트
curl http://localhost:8000/health
```

### Step 2: Docker 빌드

```bash
docker build --platform linux/amd64 -t iris-api:v1 .
docker run -d -p 8000:8000 iris-api:v1
```

### Step 3: Kubernetes 배포

```bash
export ECR_REGISTRY="<YOUR_ECR>"
export NAMESPACE="kubeflow-user01"

./scripts/build_and_deploy.sh
```

## 📊 API 명세

### GET /health
Health check 엔드포인트

### POST /predict
단일 샘플 예측

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

### POST /predict/batch
배치 예측

## ✅ 완료 체크리스트

- [ ] 모델 학습 완료
- [ ] FastAPI 서버 실행
- [ ] Docker 이미지 빌드
- [ ] Kubernetes 배포
- [ ] API 테스트 성공
