# Lab 1-1 Part 3: AWS 스토리지 확인

## 📋 개요

이 섹션에서는 MLOps 플랫폼의 AWS 스토리지 구성을 확인합니다.

**소요시간:** 15분

---

## 🎯 확인 항목

- **AWS S3 Bucket**: 객체 스토리지 (MLflow Artifacts, Pipeline Data)
- **AWS ECR**: 컨테이너 레지스트리 (ML 컨테이너 이미지)

---

## 🏗️ 스토리지 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              AWS MLOps Storage Platform                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌──────────────────┐     │
│  │   Kubeflow      │         │     MLflow       │     │
│  │   Pipeline      │────────▶│  Tracking Server │     │
│  │                 │         │    (Port 5000)   │     │
│  └─────────────────┘         └─────────┬────────┘     │
│          │                              │              │
│          │                    ┌─────────▼────────┐    │
│          │                    │    AWS RDS       │    │
│          │                    │  (PostgreSQL)    │    │
│          │                    │  or DB on EKS    │    │
│          │                    └──────────────────┘    │
│          │                                             │
│  ┌───────▼────────┐                                   │
│  │   AWS S3       │◀─────────────────────────────────│
│  │  (Artifacts)   │         (Artifact Store)          │
│  │                │                                   │
│  └────────────────┘                                   │
│                                                        │
│  ┌────────────────┐                                   │
│  │   AWS ECR      │◀─────────────────────────────────│
│  │  (Container    │      (Container Images)           │
│  │   Registry)    │                                   │
│  └────────────────┘                                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 단계별 실행

### 사전 준비

**환경 변수 설정:**

```bash
# 사용자 번호 설정 (예: 01, 02, 03...)
export USER_NUM="01"  # ⚠️ 본인 번호로 변경

# AWS 리전 설정 (선택사항, 기본값: ap-northeast-2)
export AWS_REGION="ap-northeast-2"
```

**AWS CLI 자격 증명 확인:**

```bash
# AWS 자격 증명이 올바르게 설정되어 있는지 확인
aws sts get-caller-identity
```

**예상 출력:**
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/username"
}
```

### Step 1: 자동 검증 스크립트 실행

```bash
# 검증 스크립트 실행
./3_storage_setup/verify_storage.sh
```

**예상 출력:**
```
============================================================
Lab 1-1 Part 3: AWS 스토리지 확인
============================================================

============================================================
Step 0: AWS 자격 증명 확인
============================================================
✅ AWS 자격 증명 확인 완료
   AWS Account ID: 123456789012

📋 확인할 리소스:
   🪣 S3 Bucket: mlops-training-user01
   📦 ECR Registry Prefix: mlops-user01-*
   🌏 AWS Region: ap-northeast-2

============================================================
Step 1: S3 Bucket 확인
============================================================
✅ S3 Bucket 존재: s3://mlops-training-user01
   생성 날짜: 2025-12-10T02:15:30.000Z
   리전: ap-northeast-2
   저장된 객체 수: 42

   📁 버킷 구조:
      PRE mlflow-artifacts/
      PRE kubeflow-pipeline-artifacts/

============================================================
Step 2: ECR Registry 확인
============================================================
✅ ECR Registry 발견:

   📦 Repository: mlops-user01-preprocessing
      URI: 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/mlops-user01-preprocessing
      생성 날짜: 2025-12-10
      이미지 개수: 3
      최근 태그:
         - v1.0.0
         - latest
         - dev

   📦 Repository: mlops-user01-training
      URI: 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/mlops-user01-training
      생성 날짜: 2025-12-10
      이미지 개수: 2
      최근 태그:
         - v1.0.0
         - latest

============================================================
Step 3: MLflow Artifacts 폴더 확인
============================================================
✅ MLflow Artifacts 폴더 존재: s3://mlops-training-user01/mlflow-artifacts/
   Experiment 수: 5

   📊 최근 Experiments:
      PRE 0/
      PRE 1/
      PRE 2/

============================================================
Step 4: Kubeflow Pipeline Artifacts 폴더 확인
============================================================
✅ Kubeflow Pipeline Artifacts 폴더 존재: s3://mlops-training-user01/kubeflow-pipeline-artifacts/
   Pipeline 실행 수: 3

============================================================
Step 5: AWS 스토리지 아키텍처 요약
============================================================

📊 AWS 스토리지 구성:

  ┌─────────────────────────────────────────────┐
  │       AWS MLOps Storage Architecture        │
  ├─────────────────────────────────────────────┤
  │                                             │
  │  S3 Bucket (Object Storage)                 │
  │  ├─ 버킷명: mlops-training-user01
  │  ├─ 리전: ap-northeast-2
  │  ├─ MLflow Artifacts (모델, 데이터)         │
  │  └─ Pipeline Artifacts (실행 결과)          │
  │                                             │
  │  ECR (Container Registry)                   │
  │  ├─ Registry Prefix: mlops-user01-*
  │  ├─ 리전: ap-northeast-2
  │  └─ 용도: ML 컨테이너 이미지 저장           │
  │                                             │
  └─────────────────────────────────────────────┘

============================================================
Step 6: 데이터 흐름
============================================================

1. 학습 실행
   └─▶ MLflow Tracking
       ├─▶ S3: Model 파일, Artifacts 저장
       └─▶ Metadata: Parameters, Metrics 기록

2. 모델 배포
   ├─▶ S3: 모델 파일 조회
   ├─▶ ECR: 컨테이너 이미지 저장
   └─▶ KServe: 모델 서빙

3. 파이프라인 실행
   ├─▶ S3: 입력 데이터 읽기
   ├─▶ ECR: 컴포넌트 이미지 사용
   └─▶ S3: 결과 저장

============================================================
✅ AWS 스토리지 확인 완료!
============================================================

💡 다음 단계:
   1. S3 버킷이 없다면: aws s3 mb s3://mlops-training-user01 --region ap-northeast-2
   2. ECR 레포지토리가 없다면: aws ecr create-repository --repository-name mlops-user01-app
   3. Lab 1-2로 진행: Kubeflow Pipeline 실습
```

---

## 📊 스토리지 역할

### AWS S3 (Simple Storage Service)

**버킷 이름 규칙:**
- `mlops-training-user{USER_NUM}`
- 예: `mlops-training-user01`, `mlops-training-user02`

**저장 내용:**
- **MLflow Artifacts**
  - 모델 파일 (.pkl, .h5, .pt, etc.)
  - 학습 그래프 및 시각화
  - 데이터셋 스냅샷
  - 경로: `s3://mlops-training-user01/mlflow-artifacts/`

- **Kubeflow Pipeline Artifacts**
  - 파이프라인 실행 결과
  - 중간 데이터
  - 컴포넌트 출력물
  - 경로: `s3://mlops-training-user01/kubeflow-pipeline-artifacts/`

**특징:**
- 무제한 확장성
- 99.999999999% (11 9s) 내구성
- 버전 관리 지원
- 수명 주기 정책 설정 가능

### AWS ECR (Elastic Container Registry)

**레포지토리 이름 규칙:**
- `mlops-user{USER_NUM}-{component}`
- 예: `mlops-user01-preprocessing`, `mlops-user01-training`

**저장 내용:**
- ML 컨테이너 이미지
  - 데이터 전처리 이미지
  - 모델 학습 이미지
  - 추론 서빙 이미지
- Kubeflow Pipeline 컴포넌트 이미지

**특징:**
- Docker Hub와 완전 호환
- 이미지 스캔 (보안 취약점 검사)
- 수명 주기 정책
- IAM 기반 접근 제어

---

## 🔗 데이터 흐름

### 1. 모델 학습 단계

```
Jupyter Notebook
    │
    ├─▶ MLflow Tracking
    │   ├─▶ Metadata → PostgreSQL/RDS
    │   └─▶ Model Files → S3
    │
    └─▶ Kubeflow Pipeline
        ├─▶ Component Images → ECR
        └─▶ Artifacts → S3
```

### 2. 모델 배포 단계

```
KServe InferenceService
    │
    ├─▶ 모델 조회
    │   └─▶ S3: s3://mlops-training-user01/mlflow-artifacts/.../model
    │
    └─▶ 추론 서버 이미지
        └─▶ ECR: mlops-user01-inference:latest
```

### 3. 엔드투엔드 파이프라인

```
데이터 입력
    │
    ├─▶ S3에서 데이터 로드
    │
    ├─▶ 전처리 컴포넌트 (ECR 이미지)
    │   └─▶ 결과 → S3
    │
    ├─▶ 학습 컴포넌트 (ECR 이미지)
    │   ├─▶ 모델 → S3 (MLflow)
    │   └─▶ 메트릭 → PostgreSQL
    │
    └─▶ 배포 컴포넌트
        └─▶ KServe InferenceService
```

---

## 💡 문제 해결

### 문제: AWS 자격 증명 오류

**증상:**
```
❌ AWS 자격 증명이 구성되지 않았습니다.
```

**해결:**
```bash
# AWS CLI 설정
aws configure

# 다음 정보 입력:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name: ap-northeast-2
# - Default output format: json

# 자격 증명 확인
aws sts get-caller-identity
```

### 문제: S3 버킷을 찾을 수 없음

**증상:**
```
❌ S3 Bucket을 찾을 수 없습니다: s3://mlops-training-user01
```

**해결:**
```bash
# S3 버킷 생성
aws s3 mb s3://mlops-training-user${USER_NUM} --region ap-northeast-2

# 버킷 확인
aws s3 ls s3://mlops-training-user${USER_NUM}

# 버킷 정책 설정 (필요시)
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::mlops-training-user${USER_NUM}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket mlops-training-user${USER_NUM} \
  --policy file://bucket-policy.json
```

### 문제: ECR 레포지토리가 없음

**증상:**
```
❌ ECR Registry를 찾을 수 없습니다.
```

**해결:**
```bash
# ECR 레포지토리 생성
aws ecr create-repository \
  --repository-name mlops-user${USER_NUM}-preprocessing \
  --region ap-northeast-2

aws ecr create-repository \
  --repository-name mlops-user${USER_NUM}-training \
  --region ap-northeast-2

aws ecr create-repository \
  --repository-name mlops-user${USER_NUM}-inference \
  --region ap-northeast-2

# 레포지토리 확인
aws ecr describe-repositories --region ap-northeast-2
```

### 문제: 권한 부족 오류

**증상:**
```
An error occurred (AccessDenied) when calling the ListBuckets operation
```

**해결:**

사용자에게 다음 IAM 정책이 필요합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::mlops-training-user*",
        "arn:aws:s3:::mlops-training-user*/*"
      ]
    },
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

---

## 🔒 보안 모범 사례

### S3 버킷 보안

1. **암호화 활성화**
```bash
aws s3api put-bucket-encryption \
  --bucket mlops-training-user${USER_NUM} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

2. **버전 관리 활성화**
```bash
aws s3api put-bucket-versioning \
  --bucket mlops-training-user${USER_NUM} \
  --versioning-configuration Status=Enabled
```

3. **퍼블릭 액세스 차단**
```bash
aws s3api put-public-access-block \
  --bucket mlops-training-user${USER_NUM} \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### ECR 보안

1. **이미지 스캔 활성화**
```bash
aws ecr put-image-scanning-configuration \
  --repository-name mlops-user${USER_NUM}-preprocessing \
  --image-scanning-configuration scanOnPush=true
```

2. **수명 주기 정책 설정**
```bash
cat > lifecycle-policy.json <<EOF
{
  "rules": [{
    "rulePriority": 1,
    "description": "Keep last 10 images",
    "selection": {
      "tagStatus": "any",
      "countType": "imageCountMoreThan",
      "countNumber": 10
    },
    "action": {
      "type": "expire"
    }
  }]
}
EOF

aws ecr put-lifecycle-policy \
  --repository-name mlops-user${USER_NUM}-preprocessing \
  --lifecycle-policy-text file://lifecycle-policy.json
```

---

## ✅ 완료 체크리스트

- [ ] AWS CLI 자격 증명 확인
- [ ] S3 버킷 존재 확인
- [ ] S3 버킷 리전 확인
- [ ] ECR 레포지토리 확인
- [ ] MLflow Artifacts 폴더 확인
- [ ] Kubeflow Pipeline Artifacts 폴더 확인
- [ ] 스토리지 아키텍처 이해
- [ ] 데이터 흐름 이해

---

## 🎯 학습 성과

이 섹션을 완료하면:

1. ✅ **AWS S3** - 객체 스토리지로 MLflow Artifacts 저장
2. ✅ **AWS ECR** - 컨테이너 레지스트리로 ML 이미지 관리
3. ✅ **스토리지 역할 분담** - Artifacts vs Container Images
4. ✅ **데이터 흐름** - 학습 → 저장 → 배포
5. ✅ **클라우드 네이티브 MLOps** - AWS 기반 인프라 이해

---

## 📚 다음 단계

**Lab 1-2: Hello World Pipeline** - Kubeflow Pipelines로 첫 번째 ML 워크플로우 작성

---

## 📖 참고 자료

- [AWS S3 문서](https://docs.aws.amazon.com/s3/)
- [AWS ECR 문서](https://docs.aws.amazon.com/ecr/)
- [MLflow S3 연동](https://mlflow.org/docs/latest/tracking.html#amazon-s3)
- [Kubeflow S3 연동](https://www.kubeflow.org/docs/components/pipelines/sdk/output-viewer/#s3)

---

© 2025 현대오토에버 MLOps Training
