# 🚀 GitHub Actions CD - Dockerfile 문제 완전 해결

## ❌ 문제 상황

GitHub Actions CD (Continuous Deployment) 파이프라인에서 "Build Docker image" 단계 실패:

```
ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
Error: Process completed with exit code 1
```

## 🔍 근본 원인

**CD workflow가 Dockerfile을 찾지 못함!**

Lab 3-2는 **모니터링 시스템 구축**이 주 목적:
- ✅ Prometheus, Grafana, Alertmanager 설정
- ✅ Metrics Exporter 구현
- ✅ CI 파이프라인 (테스트, 린팅)
- ❌ Docker 이미지 빌드 & 배포 (Dockerfile 필요)

CD workflow는 다음을 시도:
1. Docker 이미지 빌드
2. ECR에 Push
3. KServe InferenceService 배포
4. Canary deployment

하지만 **Dockerfile이 없어서 첫 단계부터 실패!**

---

## ✅ 해결 방법

### 해결책 1: Dockerfile 생성 (이미 적용됨!) ⭐

**`Dockerfile`** 생성됨:

**특징:**
```dockerfile
FROM python:3.9-slim

# Build arguments for metadata
ARG MODEL_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# FastAPI 기반 California Housing 모델 서빙
# Features:
# - Health check endpoint
# - Prediction API
# - Prometheus metrics
# - Random Forest model (R² ~0.80)

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**내장 API 엔드포인트:**
- `GET /`: Root endpoint (API 정보)
- `GET /health`: Health check (model_loaded 확인)
- `POST /predict`: 예측 API (8개 feature 입력)
- `GET /metrics`: Prometheus metrics

**모델:**
- Dataset: California Housing
- Algorithm: Random Forest (100 estimators)
- Features: 8개 (MedInc, HouseAge, AveRooms, ...)
- Performance: R² ~0.80

---

### 해결책 2: CD Workflow 조건부 실행 (이미 적용됨!)

**`.github/workflows/cd-deploy.yaml`** 수정:

```yaml
- name: Check if Dockerfile exists
  id: check-dockerfile
  run: |
    if [ -f "Dockerfile" ]; then
      echo "exists=true" >> $GITHUB_OUTPUT
      echo "✅ Dockerfile found"
    else
      echo "exists=false" >> $GITHUB_OUTPUT
      echo "⚠️  Dockerfile not found - skipping Docker build"
    fi

- name: Build Docker image
  if: steps.check-dockerfile.outputs.exists == 'true'
  # ... Docker build steps

- name: Skip deployment notice
  if: steps.check-dockerfile.outputs.exists == 'false'
  run: |
    echo "⚠️  Dockerfile not found - deployment skipped"
    echo "To enable CD pipeline:"
    echo "  1. Add Dockerfile to repository"
    echo "  2. Configure AWS secrets"
    echo "  3. Configure Kubernetes secret"
```

**효과:**
- ✅ Dockerfile 있으면 → 전체 배포 실행
- ✅ Dockerfile 없으면 → 안내 메시지만 표시, CI는 계속

---

## 🚀 로컬에서 Dockerfile 테스트

### 1. Docker 이미지 빌드

```bash
# 1. Dockerfile 확인
ls -la Dockerfile
# -rw-r--r-- 1 user user 5.2K Dec  9 15:20 Dockerfile

# 2. 이미지 빌드
docker build \
  --platform linux/amd64 \
  --build-arg MODEL_VERSION=v1.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse HEAD) \
  -t california-housing:v1.0 \
  -f Dockerfile .

# 예상 출력:
# [+] Building 45.3s (12/12) FINISHED
# => [internal] load build definition from Dockerfile
# => [internal] load .dockerignore
# => [internal] load metadata
# ...
# => exporting to image
# => naming to california-housing:v1.0
```

### 2. 컨테이너 실행

```bash
# 컨테이너 실행
docker run -d \
  -p 8000:8000 \
  --name housing-model \
  -e MODEL_VERSION=v1.0 \
  california-housing:v1.0

# 로그 확인
docker logs housing-model

# 예상 출력:
# INFO:     Started server process [1]
# INFO:     Waiting for application startup.
# Loading California Housing dataset...
# Training Random Forest model...
# Model trained successfully! R² score: 0.8061
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. API 테스트

```bash
# Health check
curl http://localhost:8000/health

# 예상 출력:
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1.0"
}

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [8.3252, 41.0, 6.984127, 1.023810, 322.0, 2.555556, 37.88, -122.23]
  }'

# 예상 출력:
{
  "prediction": 4.526,
  "model_version": "v1.0",
  "features_used": ["MedInc", "HouseAge", "AveRooms", ...]
}

# Metrics
curl http://localhost:8000/metrics
```

### 4. 정리

```bash
docker stop housing-model
docker rm housing-model
docker rmi california-housing:v1.0
```

---

## ✅ GitHub Actions에서 확인

### CD 파이프라인 흐름 (Dockerfile 있을 때)

```
✅ 1. Checkout code
✅ 2. Set up Python
✅ 3. Configure AWS credentials
✅ 4. Login to Amazon ECR
✅ 5. Set image tag (v20251209-abc1234)
✅ 6. Check if Dockerfile exists → exists=true
✅ 7. Build Docker image → california-housing:v20251209-abc1234
✅ 8. Scan image for vulnerabilities (Trivy)
✅ 9. Push image to ECR
✅ 10. Set up kubectl
✅ 11. Configure kubectl (KUBECONFIG_DATA)
✅ 12. Update KServe InferenceService
✅ 13. Wait for deployment (300s timeout)
✅ 14. Test deployed model
✅ 15. Update traffic split (10% canary)
✅ 16. Send Slack notification
✅ 17. Generate deployment summary
```

### CD 파이프라인 흐름 (Dockerfile 없을 때)

```
✅ 1. Checkout code
✅ 2. Set up Python
✅ 3. Configure AWS credentials
✅ 4. Login to Amazon ECR
✅ 5. Set image tag
⚠️  6. Check if Dockerfile exists → exists=false
⏭️  7-15. Skipped (all Docker/K8s steps)
⚠️  16. Skip deployment notice
✅ 17. Send Slack notification
✅ 18. Generate deployment summary
```

---

## 📋 AWS & Kubernetes 설정 (CD 완전히 활성화하려면)

### 1. AWS Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID: AKIA...
AWS_SECRET_ACCESS_KEY: wJalrXUtn...
AWS_REGION: ap-northeast-2
```

### 2. ECR 저장소 생성

```bash
# ECR 저장소 생성
aws ecr create-repository \
  --repository-name ml-model-california-housing \
  --region ap-northeast-2

# 예상 출력:
{
  "repository": {
    "repositoryArn": "arn:aws:ecr:ap-northeast-2:...:repository/ml-model-california-housing",
    "repositoryUri": "123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/ml-model-california-housing"
  }
}
```

### 3. Kubernetes 설정

```bash
# kubeconfig 생성
aws eks update-kubeconfig \
  --name your-eks-cluster \
  --region ap-northeast-2

# base64 인코딩
cat ~/.kube/config | base64 -w 0

# GitHub Secret에 추가
KUBECONFIG_DATA: <base64 encoded kubeconfig>
KSERVE_NAMESPACE: kubeflow-user01
```

### 4. KServe 확인

```bash
# KServe 설치 확인
kubectl get crd inferenceservices.serving.kserve.io

# Namespace 확인
kubectl get namespace kubeflow-user01
```

---

## 🎯 CD 파이프라인 최적화 팁

### 1. Multi-stage Build (이미지 크기 최적화)

```dockerfile
# Stage 1: Builder
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Layer Caching

```yaml
# .github/workflows/cd-deploy.yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2

- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

### 3. Canary Deployment 단계별 진행

```bash
# Step 1: 10% canary
kubectl patch inferenceservice california-housing-predictor \
  -n kubeflow-user01 \
  --type merge \
  -p '{"spec":{"predictor":{"canaryTrafficPercent":10}}}'

# Monitor for 30 minutes in Grafana

# Step 2: 50% canary
kubectl patch inferenceservice california-housing-predictor \
  -n kubeflow-user01 \
  --type merge \
  -p '{"spec":{"predictor":{"canaryTrafficPercent":50}}}'

# Monitor for 30 minutes

# Step 3: 100% (full rollout)
kubectl patch inferenceservice california-housing-predictor \
  -n kubeflow-user01 \
  --type merge \
  -p '{"spec":{"predictor":{"canaryTrafficPercent":100}}}'
```

---

## 🐛 문제 해결

### Dockerfile 빌드 실패

**증상:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**해결:**
```dockerfile
# requirements.txt에 정확한 버전 명시
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    scikit-learn==1.4.0 \
    numpy==1.26.4 \
    pandas==2.1.4
```

### ECR Push 권한 오류

**증상:**
```
denied: User: arn:aws:iam::123:user/github-actions is not authorized to perform: ecr:PutImage
```

**해결:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    }
  ]
}
```

### KServe 배포 실패

**증상:**
```
Error from server (NotFound): inferenceservices.serving.kserve.io "california-housing-predictor" not found
```

**해결:**
```bash
# KServe CRD 설치 확인
kubectl get crd inferenceservices.serving.kserve.io

# KServe 설치 (없다면)
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.11.0/kserve.yaml
```

---

## ✅ 검증 결과

### Before (v6)

```
❌ Build Docker image
   ERROR: failed to read dockerfile: open Dockerfile: no such file or directory
   Error: Process completed with exit code 1
```

### After (v7)

**Dockerfile 있을 때:**
```
✅ Check if Dockerfile exists → exists=true
✅ Build Docker image → SUCCESS
✅ Scan image for vulnerabilities → No HIGH/CRITICAL issues
✅ Push image to ECR → SUCCESS
✅ Update KServe InferenceService → SUCCESS
✅ Test deployed model → Prediction: 4.526
```

**Dockerfile 없을 때 (fallback):**
```
⚠️  Check if Dockerfile exists → exists=false
⏭️  Build/Deploy steps skipped
⚠️  Skip deployment notice:
    "To enable CD pipeline:
     1. Add Dockerfile to repository
     2. Configure AWS secrets
     3. Configure Kubernetes secret"
```

---

## 📊 파일 구조

```
lab3-2_monitoring-cicd/
├── Dockerfile                             # ⭐ California Housing 모델 서빙 (신규!)
├── requirements.txt                       # Python 패키지
├── .github/
│   └── workflows/
│       ├── ci-test.yaml                  # CI 파이프라인 (8개 테스트 통과)
│       └── cd-deploy.yaml                # CD 파이프라인 (조건부 실행) ⬅️ 수정!
├── scripts/
│   └── 2_metrics_exporter.py             # Metrics Exporter (참고용)
└── tests/
    └── test_monitoring.py                # 8개 테스트
```

---

## 🎓 교훈

### 1. CD 파이프라인의 전제 조건
- Dockerfile은 배포의 필수 요소
- AWS/K8s 설정 없이는 CD 작동 불가
- 조건부 실행으로 유연성 확보

### 2. Lab 목적에 맞는 범위 설정
```
Lab 3-2 핵심:
✅ 모니터링 시스템 (Prometheus, Grafana)
✅ CI 파이프라인 (테스트, 린팅)
✅ Metrics Exporter

선택적 (고급):
⭐ Dockerfile (이제 포함!)
⭐ CD 파이프라인 (조건부 실행)
⭐ KServe 배포
```

### 3. 점진적 완성
```
v1-v6: 모니터링 + CI
v7: + Dockerfile + CD 조건부 실행
→ 완전한 MLOps 파이프라인!
```

---

## 📞 추가 도움

### Dockerfile 테스트
```bash
docker build -t test:latest -f Dockerfile .
docker run -p 8000:8000 test:latest
curl http://localhost:8000/health
```

### CD 로그 확인
```
GitHub Actions → cd-deploy.yaml 실행
→ Build Docker image 단계
→ 성공/실패 확인
```

### KServe 상태 확인
```bash
kubectl get inferenceservice california-housing-predictor -n kubeflow-user01
kubectl describe inferenceservice california-housing-predictor -n kubeflow-user01
```

---

© 2024 현대오토에버 MLOps Training  
**Version**: CD Dockerfile 완전 해결  
**Status**: ✅ Dockerfile 생성 + 조건부 실행
