# Lab 1-1: AWS EKS 환경 설정

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 30분 |
| **난이도** | ⭐ |
| **목표** | AWS CLI 설정 및 EKS 클러스터 연결 |

## 🎯 학습 목표

- AWS CLI 자격 증명 설정
- EKS 클러스터 kubeconfig 업데이트
- kubectl로 클러스터 연결 확인
- 네임스페이스 접근 권한 확인

## 📝 사전 요구사항

- AWS CLI v2 설치
- kubectl 설치
- 제공된 AWS Access Key / Secret Key

## 🔧 실습 단계

### Step 1: AWS CLI 자격 증명 설정

```bash
aws configure
# AWS Access Key ID: [제공된 Access Key]
# AWS Secret Access Key: [제공된 Secret Key]
# Default region name: ap-northeast-2
# Default output format: json
```

### Step 2: 자격 증명 확인

```bash
aws sts get-caller-identity
```

예상 출력:
```json
{
    "UserId": "AIDAXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/mlops-userXX"
}
```

### Step 3: EKS 클러스터 연결

```bash
aws eks update-kubeconfig \
    --region ap-northeast-2 \
    --name mlops-training-cluster
```

### Step 4: 연결 확인

```bash
# 노드 목록 확인
kubectl get nodes

# 네임스페이스 목록 확인
kubectl get namespaces

# 내 네임스페이스 확인
kubectl get pods -n kubeflow-userXX
```

## ✅ 완료 체크리스트

- [ ] `aws sts get-caller-identity` 성공
- [ ] `kubectl get nodes` 노드 목록 출력
- [ ] 내 네임스페이스 접근 가능

## ❓ 트러블슈팅

### 문제: "Unable to locate credentials"

```bash
# 자격 증명 파일 확인
cat ~/.aws/credentials

# 환경 변수 확인
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### 문제: "error: You must be logged in to the server"

```bash
# kubeconfig 재설정
aws eks update-kubeconfig --region ap-northeast-2 --name mlops-training-cluster

# 컨텍스트 확인
kubectl config current-context
```

## 📚 참고 자료

- [AWS CLI 설치 가이드](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [EKS 시작하기](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html)
