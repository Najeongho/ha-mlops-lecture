# Kubernetes Manifests

이 디렉토리는 MLOps 교육에서 사용하는 Kubernetes 매니페스트 파일들을 포함합니다.

## 📁 디렉토리 구조

```
manifests/
├── deployments/
│   └── fastapi-deployment.yaml    # FastAPI 모델 서버 Deployment
├── services/
│   └── fastapi-service.yaml       # FastAPI Service (ClusterIP, NodePort)
├── kserve/
│   └── sklearn-inferenceservice.yaml  # KServe InferenceService
└── README.md
```

## 🚀 사용 방법

### 1. 네임스페이스 설정

```bash
export NAMESPACE=kubeflow-user01  # 본인 네임스페이스로 변경
```

### 2. Deployment & Service 배포

```bash
# FastAPI 모델 서버 배포
kubectl apply -f deployments/fastapi-deployment.yaml -n $NAMESPACE
kubectl apply -f services/fastapi-service.yaml -n $NAMESPACE

# 상태 확인
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
```

### 3. KServe InferenceService 배포

```bash
# InferenceService 배포
kubectl apply -f kserve/sklearn-inferenceservice.yaml -n $NAMESPACE

# 상태 확인
kubectl get inferenceservice -n $NAMESPACE
```

## ⚙️ 설정 변경

배포 전 다음 항목을 본인 환경에 맞게 수정하세요:

### deployments/fastapi-deployment.yaml
- `image`: ECR 또는 Docker Hub 이미지 URI

### kserve/sklearn-inferenceservice.yaml
- `storageUri`: S3 모델 경로

## 📋 주요 명령어

```bash
# 리소스 조회
kubectl get all -n $NAMESPACE

# Pod 로그 확인
kubectl logs <pod-name> -n $NAMESPACE

# Pod 상세 정보
kubectl describe pod <pod-name> -n $NAMESPACE

# 포트 포워딩
kubectl port-forward svc/fastapi-model-service 8080:80 -n $NAMESPACE

# 리소스 삭제
kubectl delete -f deployments/ -n $NAMESPACE
kubectl delete -f services/ -n $NAMESPACE
kubectl delete -f kserve/ -n $NAMESPACE
```

## 🔍 문제 해결

### Pod가 시작되지 않을 때

```bash
# 이벤트 확인
kubectl describe pod <pod-name> -n $NAMESPACE

# 이미지 풀 오류인 경우
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'
```

### InferenceService가 Ready 상태가 되지 않을 때

```bash
# 상세 상태 확인
kubectl describe inferenceservice <name> -n $NAMESPACE

# Predictor Pod 로그 확인
kubectl logs -l serving.kserve.io/inferenceservice=<name> -n $NAMESPACE
```
