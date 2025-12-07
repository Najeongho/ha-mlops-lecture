# Lab 2-3: KServe 배포

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 40분 |
| **난이도** | ⭐⭐⭐ |
| **목표** | KServe InferenceService로 모델 배포 및 Canary 전략 적용 |

## 🎯 학습 목표

- KServe InferenceService 생성
- Sklearn 모델 배포
- Canary 배포 전략 적용
- 트래픽 분할 및 롤백

## 🏗️ 아키텍처

```
                    ┌─────────────────────────────────────────┐
                    │         KServe InferenceService         │
┌──────────┐        │  ┌─────────────────────────────────────┐│
│  Client  │───────▶│  │         Knative Serving             ││
│  (curl)  │        │  │  ┌───────────┐    ┌───────────┐    ││
└──────────┘        │  │  │ Default   │    │  Canary   │    ││
                    │  │  │   (90%)   │    │   (10%)   │    ││
                    │  │  │ sklearn   │    │ sklearn   │    ││
                    │  │  │   v1      │    │   v2      │    ││
                    │  │  └───────────┘    └───────────┘    ││
                    │  └─────────────────────────────────────┘│
                    └─────────────────────────────────────────┘
```

## 📁 파일 구조

```
lab2-3_kserve-deploy/
├── README.md
├── inference-service.yaml         # 기본 InferenceService
├── inference-service-canary.yaml  # Canary 배포
├── test_inference.sh              # API 테스트 스크립트
└── deploy.sh                      # 배포 스크립트
```

## 🔧 실습 단계

### Step 1: 모델 S3 업로드 (이미 완료된 경우 생략)

```bash
# MLflow에서 모델을 S3로 복사
aws s3 cp --recursive \
    s3://mlflow-artifacts/[run-id]/artifacts/model \
    s3://mlops-training-models/california/
```

### Step 2: InferenceService 생성

```bash
# YAML 파일 수정 (namespace, storageUri)
vim inference-service.yaml

# 배포
kubectl apply -f inference-service.yaml

# 상태 확인
kubectl get isvc california-model -n kubeflow-userXX
```

### Step 3: READY 상태 대기

```bash
# 상태 모니터링 (READY=True까지)
kubectl get isvc california-model -n kubeflow-userXX -w

# 상세 정보 확인
kubectl describe isvc california-model -n kubeflow-userXX
```

### Step 4: API 테스트

```bash
# 포트 포워딩
kubectl port-forward svc/california-model-predictor-default \
    -n kubeflow-userXX 8080:80

# 테스트
./test_inference.sh
```

### Step 5: Canary 배포 (선택)

```bash
# Canary 배포 적용
kubectl apply -f inference-service-canary.yaml

# 트래픽 분배 확인
kubectl get isvc california-model -n kubeflow-userXX
```

## ✅ 완료 체크리스트

- [ ] InferenceService YAML 작성
- [ ] kubectl apply 성공
- [ ] READY=True 상태 확인
- [ ] /predict 엔드포인트 테스트 성공
- [ ] (선택) Canary 배포 적용

## 📊 API 명세

### POST /v1/models/california-model:predict

**Request:**
```json
{
  "instances": [
    [8.3252, 41.0, 6.984, 1.024, 322.0, 2.556, 37.88, -122.23]
  ]
}
```

**Response:**
```json
{
  "predictions": [4.526]
}
```

## ❓ 트러블슈팅

### 문제: READY=False 지속

```bash
# Pod 상태 확인
kubectl get pods -n kubeflow-userXX | grep california

# 이벤트 확인
kubectl describe isvc california-model -n kubeflow-userXX
```

### 문제: storageUri 접근 실패

```bash
# S3 버킷 권한 확인
aws s3 ls s3://mlops-training-models/california/

# ServiceAccount IAM 역할 확인
kubectl describe sa default -n kubeflow-userXX
```

### 문제: "502 Bad Gateway"

```bash
# Predictor Pod 로그 확인
kubectl logs -l serving.kserve.io/inferenceservice=california-model \
    -n kubeflow-userXX
```

## 📚 참고 자료

- [KServe 공식 문서](https://kserve.github.io/website/)
- [InferenceService API](https://kserve.github.io/website/0.10/reference/api/)
