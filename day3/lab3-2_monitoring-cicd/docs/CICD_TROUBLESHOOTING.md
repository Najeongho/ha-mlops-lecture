# CI/CD 파이프라인 트러블슈팅 가이드

> Lab 3-2 실습 중 발생할 수 있는 CI/CD 관련 문제 해결 가이드

---

## 📋 목차

1. [문제 1: ECR Repository 없음](#문제-1-ecr-repository-없음)
2. [문제 2: Pod Pending 상태](#문제-2-pod-pending-상태)
3. [문제 3: Health Check 000 반환](#문제-3-health-check-000-반환)
4. [문제 4: ImagePullBackOff](#문제-4-imagepullbackoff)
5. [문제 5: KUBECONFIG 인증 실패](#문제-5-kubeconfig-인증-실패)

---

## 문제 1: ECR Repository 없음

### 증상

```
Error: Cannot perform an interactive login from a non TTY device
denied: Your authorization token has expired. Reauthenticate and try again.
```

또는

```
name unknown: The repository with name 'ml-model-california-housing' does not exist
```

### 원인

GitHub Actions CD 파이프라인에서 Docker 이미지를 ECR에 Push하려고 할 때, 
ECR Repository가 존재하지 않으면 Push가 실패합니다.

### 해결 방법

#### 방법 A: AWS Console에서 수동 생성

1. AWS Console 로그인
2. ECR (Elastic Container Registry) 서비스로 이동
3. 'Create repository' 클릭
4. Repository 이름: `ml-model-california-housing`
5. 'Scan on push' 활성화
6. 'Create repository' 클릭

#### 방법 B: AWS CLI로 생성

```bash
aws ecr create-repository \
  --repository-name ml-model-california-housing \
  --image-scanning-configuration scanOnPush=true \
  --region ap-northeast-2

# 확인
aws ecr describe-repositories --repository-names ml-model-california-housing
```

#### 방법 C: CD 파이프라인에 자동 생성 로직 추가 (권장)

```yaml
- name: Create ECR Repository if not exists
  run: |
    if aws ecr describe-repositories --repository-names $ECR_REPOSITORY 2>/dev/null; then
      echo "✅ ECR repository already exists"
    else
      aws ecr create-repository \
        --repository-name $ECR_REPOSITORY \
        --image-scanning-configuration scanOnPush=true \
        --image-tag-mutability MUTABLE
      echo "✅ ECR repository created"
    fi
```

---

## 문제 2: Pod Pending 상태

### 증상

```
error: unable to forward port because pod is not running. Current status=Pending
curl: (7) Failed to connect to localhost port 8000
❌ Health check failed
```

### 원인

1. **이미지 Pull 지연**: ECR에서 이미지를 다운로드하는 데 시간이 걸림
2. **리소스 부족**: 노드의 CPU/메모리 리소스가 부족
3. **스케줄링 지연**: Kubernetes 스케줄러가 적절한 노드를 찾는 중

### 해결 방법

#### kubectl wait 사용 (권장)

```yaml
- name: Wait for Pod to be Ready
  run: |
    # Pod 생성 대기
    MAX_WAIT=60
    WAITED=0
    while [ $WAITED -lt $MAX_WAIT ]; do
      POD_NAME=$(kubectl get pods -n $NAMESPACE \
        -l serving.kserve.io/inferenceservice=california-housing-predictor \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
      
      if [ -n "$POD_NAME" ]; then
        echo "✅ Pod found: $POD_NAME"
        break
      fi
      
      sleep 5
      WAITED=$((WAITED + 5))
    done
    
    # kubectl wait로 Ready 상태 대기
    kubectl wait --for=condition=Ready pod/$POD_NAME -n $NAMESPACE --timeout=600s
```

#### 디버깅 명령어

```bash
# Pod 상태 확인
kubectl get pods -n kubeflow-user01 -l serving.kserve.io/inferenceservice=california-housing-predictor

# Pod 이벤트 확인
kubectl describe pod <pod-name> -n kubeflow-user01

# 노드 리소스 확인
kubectl describe nodes | grep -A 5 "Allocated resources"
```

---

## 문제 3: Health Check 000 반환

### 증상

```
INFO:     192.168.15.255:59564 - "GET /health HTTP/1.1" 200 OK  ← 성공!
Health endpoint returned: 000  ← 실패?
```

로그에서는 200 OK인데, Health Check 결과는 000을 반환하는 모순적인 상황

### 원인

**`python:3.9-slim` Docker 이미지에는 `curl`이 설치되어 있지 않습니다!**

```bash
kubectl exec $POD -- curl http://localhost:8080/health
# → "curl: command not found" → exit code 127 → HTTP code "000"
```

`192.168.15.255`에서 오는 요청은 Kubernetes의 **readinessProbe**입니다.
Pod 내부 앱은 정상 작동 중이지만, `curl` 명령이 없어서 kubectl exec가 실패한 것입니다.

### 해결 방법

#### Python urllib 사용 (권장)

```yaml
- name: Verify application health
  run: |
    kubectl exec -n $NAMESPACE $POD_NAME -- python -c "
    import urllib.request
    import json
    response = urllib.request.urlopen('http://localhost:8080/health', timeout=10)
    data = json.loads(response.read().decode())
    print(json.dumps(data, indent=2))
    if data.get('model_loaded'):
        print('✅ Model is loaded and ready!')
    "
```

#### 네트워크 구성 이해

```
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions Runner (외부망)                               │
│                                                              │
│   kubectl exec ──────────────────────────────────────────┐  │
│                                                          │  │
└──────────────────────────────────────────────────────────┼──┘
                                                           │
                    ┌──────────────────────────────────────┼──┐
                    │ AWS EKS Cluster                      │  │
                    │                                      ▼  │
                    │  ┌─────────────────────────────────────┐│
                    │  │ Pod: california-housing-predictor   ││
                    │  │                                     ││
                    │  │  ┌─────────────────────────────┐   ││
                    │  │  │ Container                   │   ││
                    │  │  │ - Python ✅                 │   ││
                    │  │  │ - curl ❌ (설치 안됨)       │   ││
                    │  │  │ - FastAPI (port 8080)      │   ││
                    │  │  └─────────────────────────────┘   ││
                    │  │                                     ││
                    │  │  readinessProbe (192.168.x.x)      ││
                    │  │  → GET /health → 200 OK ✅         ││
                    │  └─────────────────────────────────────┘│
                    └─────────────────────────────────────────┘
```

---

## 문제 4: ImagePullBackOff

### 증상

```bash
$ kubectl get pods -n kubeflow-user01
NAME                                              READY   STATUS             RESTARTS   AGE
california-housing-predictor-xxx                  0/1     ImagePullBackOff   0          5m
```

### 원인

1. ECR 이미지 경로가 잘못됨
2. ECR 인증 실패
3. 이미지가 존재하지 않음

### 해결 방법

#### 이미지 존재 확인

```bash
aws ecr describe-images \
  --repository-name ml-model-california-housing \
  --region ap-northeast-2
```

#### ECR 로그인 테스트

```bash
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com
```

#### Pod 이벤트 확인

```bash
kubectl describe pod <pod-name> -n kubeflow-user01 | grep -A 10 "Events:"
```

---

## 문제 5: KUBECONFIG 인증 실패

### 증상

```
error: You must be logged in to the server (Unauthorized)
```

### 원인

1. KUBECONFIG_DATA Secret이 설정되지 않음
2. Base64 인코딩이 잘못됨
3. kubeconfig의 토큰이 만료됨

### 해결 방법

#### KUBECONFIG 재생성

```bash
# 1. EKS 클러스터 kubeconfig 업데이트
aws eks update-kubeconfig \
  --name mlops-training-cluster \
  --region ap-northeast-2

# 2. Base64 인코딩 (한 줄로)
cat ~/.kube/config | base64 -w 0 > kubeconfig_base64.txt

# 3. GitHub Secret에 붙여넣기
cat kubeconfig_base64.txt
```

#### 인코딩 확인

```bash
# 디코딩 테스트
echo "$(cat kubeconfig_base64.txt)" | base64 -d | head -10
```

#### aws-iam-authenticator 설치 확인

CD 파이프라인에서 aws-iam-authenticator가 설치되어야 합니다:

```yaml
- name: Install aws-iam-authenticator
  run: |
    curl -Lo aws-iam-authenticator \
      https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.6.11/aws-iam-authenticator_0.6.11_linux_amd64
    chmod +x ./aws-iam-authenticator
    sudo mv ./aws-iam-authenticator /usr/local/bin/
    aws-iam-authenticator version
```

---

## 📊 문제 해결 흐름도

```
CD 파이프라인 실패
        │
        ▼
┌───────────────────┐
│ 어느 단계에서 실패? │
└───────────────────┘
        │
        ├─── ECR Push 실패 ──────────► ECR Repository 생성 (문제 1)
        │
        ├─── Pod Pending ────────────► kubectl wait 추가 (문제 2)
        │
        ├─── Health Check 000 ───────► Python urllib 사용 (문제 3)
        │
        ├─── ImagePullBackOff ───────► ECR 권한/경로 확인 (문제 4)
        │
        └─── Unauthorized ───────────► KUBECONFIG 재생성 (문제 5)
```

---

## ✅ 최종 수정 사항 요약

| 항목 | 기존 | 수정 후 |
|------|------|---------|
| ECR Repository | 수동 생성 필요 | 자동 생성 |
| Pod Ready 대기 | 없음 | `kubectl wait --for=condition=Ready` |
| Health Check | `curl` (실패) | `python urllib` (성공) |
| Startup Probe | 없음 | 최대 5분 대기 |
| 리소스 요청 | 256Mi | 512Mi |

---

## 📞 지원

문제가 지속될 경우:

1. GitHub Actions 로그 전체 캡처
2. `kubectl describe pod` 출력
3. `kubectl logs` 출력
4. Slack #mlops-training 채널에 공유
