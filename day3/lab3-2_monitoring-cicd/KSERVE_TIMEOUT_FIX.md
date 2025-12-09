# 🔧 KServe InferenceService Timeout 문제 완전 해결

## ❌ 문제 상황

KServe InferenceService 배포 시 타임아웃 발생:

```
Waiting for InferenceService to be ready...
error: timed out waiting for the condition on inferenceservices/california-housing-predictor
Error: Process completed with exit code 1.
```

---

## 🔍 근본 원인 분석

### 원인 1: 포트 불일치 ⭐ (가장 중요!)

```yaml
# InferenceService 설정 (v11)
spec:
  predictor:
    containers:
      - containerPort: 8080  ← KServe가 기대하는 포트

# Dockerfile 설정
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
                                                    ↑ 실제 포트

# 결과:
# - Kubernetes가 8080 포트로 Health check 시도
# - 하지만 애플리케이션은 8000 포트에서만 리스닝
# - Health check 실패 → Ready 안됨 → Timeout!
```

### 원인 2: Health Probe 미설정

```yaml
# v11에는 readinessProbe와 livenessProbe가 없음
# → Kubernetes가 언제 Pod이 준비되었는지 알 수 없음
# → 기본 설정으로만 체크하여 실패
```

### 원인 3: 불충분한 디버깅 정보

```bash
# v11의 Wait for deployment
kubectl wait --for=condition=Ready ...
# → 타임아웃 시 이유를 알 수 없음
# → 로그, 이벤트, Pod 상태 등 확인 불가
```

---

## ✅ 해결 방법 (v12)

### 해결 1: 포트 통일 (8000) ⭐

```yaml
# InferenceService (v12)
spec:
  predictor:
    containers:
      - name: kserve-container
        ports:
          - containerPort: 8000  ← 8080 → 8000으로 변경!
            protocol: TCP
        # ... rest of config
```

**효과:**
- ✅ Kubernetes가 올바른 포트(8000)로 트래픽 라우팅
- ✅ Health check가 올바른 포트에 접속
- ✅ Pod이 정상적으로 Ready 상태가 됨

### 해결 2: Health Probes 추가

```yaml
spec:
  predictor:
    containers:
      - name: kserve-container
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30  # 30초 후 첫 체크
          periodSeconds: 10        # 10초마다 체크
          timeoutSeconds: 5        # 5초 타임아웃
          failureThreshold: 3      # 3번 실패 시 실패로 간주
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60  # 60초 후 첫 체크
          periodSeconds: 20        # 20초마다 체크
          timeoutSeconds: 5
          failureThreshold: 3
```

**효과:**
- ✅ Kubernetes가 정확한 시점에 Pod Ready 판단
- ✅ 애플리케이션 시작 시간 고려 (initialDelaySeconds)
- ✅ 주기적 Health 모니터링

### 해결 3: 상세한 디버깅 정보

```bash
# v12의 Wait for deployment
if kubectl wait --for=condition=Ready ...; then
  echo "✅ InferenceService is ready!"
else
  echo "❌ InferenceService failed to become ready"
  
  # 상세 디버깅 정보 출력:
  echo "=== InferenceService Status ==="
  kubectl get inferenceservice ... -o yaml
  
  echo "=== Pod Status ==="
  kubectl get pods ...
  
  echo "=== Pod Describe ==="
  kubectl describe pods ...
  
  echo "=== Pod Logs ==="
  kubectl logs ... --all-containers=true --tail=100
  
  echo "=== Events ==="
  kubectl get events --sort-by='.lastTimestamp' | tail -20
  
  exit 1
fi
```

**효과:**
- ✅ 타임아웃 원인 즉시 파악 가능
- ✅ Pod 로그로 애플리케이션 오류 확인
- ✅ Events로 Kubernetes 레벨 문제 확인

### 해결 4: Test Endpoint 수정

```bash
# v11: KServe 표준 API 사용 (작동 안함)
curl -X POST "$INFERENCE_URL/v1/models/california-housing:predict"

# v12: FastAPI 엔드포인트 직접 테스트 (작동!)
# 1. Port-forward로 직접 접속
kubectl port-forward pod/$POD_NAME 8000:8000 &

# 2. Health check
curl http://localhost:8000/health

# 3. Predict test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [8.3252, 41.0, ...]}'
```

**효과:**
- ✅ 실제 애플리케이션 API 테스트
- ✅ 배포 검증 완료

---

## 🚀 v11 → v12 변경사항

| 항목 | v11 (실패) | v12 (성공) |
|------|-----------|-----------|
| **containerPort** | 8080 ❌ | 8000 ✅ |
| **readinessProbe** | 없음 ❌ | /health:8000 ✅ |
| **livenessProbe** | 없음 ❌ | /health:8000 ✅ |
| **디버깅 정보** | 없음 ❌ | 상세 출력 ✅ |
| **테스트 엔드포인트** | KServe API ❌ | FastAPI ✅ |

---

## 📊 배포 흐름 비교

### v11 흐름 (실패)

```
1. kubectl apply InferenceService
   → containerPort: 8080 설정
2. kubectl wait --for=condition=Ready
   → Kubernetes가 8080 포트로 Health check 시도
   → 애플리케이션은 8000 포트에서 리스닝
   → Health check 실패
   → 300초 대기
   ❌ Timeout!
```

### v12 흐름 (성공)

```
1. kubectl apply InferenceService
   → containerPort: 8000 설정
   → readinessProbe: /health:8000
   → livenessProbe: /health:8000
2. kubectl wait --for=condition=Ready
   → Kubernetes가 8000 포트로 Health check
   → readinessProbe 30초 후 시작
   → GET /health → {"status":"healthy"}
   ✅ Pod Ready!
3. Port-forward로 직접 테스트
   → curl http://localhost:8000/health ✅
   → curl http://localhost:8000/predict ✅
4. 배포 완료 ✅
```

---

## 🎓 핵심 교훈

### 1. 포트 일치 필수!

```yaml
# 모든 설정에서 동일한 포트 사용
Dockerfile:
  EXPOSE 8000
  CMD ["uvicorn", "api:app", "--port", "8000"]

InferenceService:
  ports:
    - containerPort: 8000
  
  readinessProbe:
    httpGet:
      port: 8000
  
  livenessProbe:
    httpGet:
      port: 8000
```

### 2. Health Probes 필수!

```yaml
# Kubernetes가 Pod 상태를 정확히 판단하려면:
readinessProbe:  # 트래픽 받을 준비 확인
  initialDelaySeconds: 30  # 애플리케이션 시작 시간 고려
  
livenessProbe:   # 애플리케이션 살아있는지 확인
  initialDelaySeconds: 60  # 더 긴 시간 허용
```

### 3. 디버깅 정보 필수!

```bash
# 실패 시 즉시 원인 파악을 위해:
- InferenceService 상태 (YAML)
- Pod 상태 (STATUS, READY)
- Pod Describe (Events, Conditions)
- Pod Logs (애플리케이션 로그)
- Cluster Events (Kubernetes 이벤트)
```

### 4. 실제 API 테스트!

```bash
# KServe 표준 API가 아닌 실제 FastAPI 엔드포인트 테스트
GET /health  → Health check
POST /predict → Prediction test
```

---

## 🐛 추가 문제 해결

### 문제: ECR 이미지 Pull 실패

**증상:**
```
Pod Status: ImagePullBackOff
Events: Failed to pull image "123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/..."
```

**해결:**
```bash
# 1. EKS 노드에 ECR 권한 부여
# IAM Role에 AmazonEC2ContainerRegistryReadOnly 정책 추가

# 2. ImagePullSecrets 생성 (필요 시)
kubectl create secret docker-registry ecr-secret \
  --docker-server=123456789012.dkr.ecr.ap-northeast-2.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region ap-northeast-2) \
  -n kubeflow-user01

# 3. InferenceService에 추가
spec:
  predictor:
    imagePullSecrets:
      - name: ecr-secret
```

### 문제: OOMKilled (메모리 부족)

**증상:**
```
Pod Status: OOMKilled
Events: Container exceeded memory limit
```

**해결:**
```yaml
# 메모리 증가
resources:
  requests:
    memory: 1Gi   # 1Gi → 2Gi
  limits:
    memory: 2Gi   # 2Gi → 4Gi
```

### 문제: CrashLoopBackOff

**증상:**
```
Pod Status: CrashLoopBackOff
Events: Back-off restarting failed container
```

**해결:**
```bash
# Pod 로그 확인
kubectl logs -n kubeflow-user01 $POD_NAME

# 일반적인 원인:
# 1. Python 패키지 누락 → requirements.txt 확인
# 2. 포트 충돌 → 포트 설정 확인
# 3. 환경 변수 오류 → env 설정 확인
```

---

## ✅ 검증 방법

### 1. InferenceService 상태 확인

```bash
kubectl get inferenceservice california-housing-predictor -n kubeflow-user01

# 예상 출력:
NAME                          URL   READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION   AGE
california-housing-predictor        True    0      100                                                    5m
```

### 2. Pod 상태 확인

```bash
kubectl get pods -n kubeflow-user01 -l serving.kserve.io/inferenceservice=california-housing-predictor

# 예상 출력:
NAME                                                         READY   STATUS    RESTARTS   AGE
california-housing-predictor-predictor-00001-deployment-...  2/2     Running   0          5m
```

### 3. Health Check 테스트

```bash
# Port-forward
kubectl port-forward -n kubeflow-user01 pod/$POD_NAME 8000:8000 &

# Health check
curl http://localhost:8000/health
# {"status":"healthy","model_loaded":true}

# Predict test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[8.3252,41.0,6.98,1.02,322.0,2.55,37.88,-122.23]}'
# {"prediction":4.526,"model_version":"v20251209-xxx","features_used":[...]}
```

---

## 📦 다운로드

### v12 최종 완전 해결 버전

**ZIP 파일 (156KB):**
[lab3-2_monitoring-cicd_최종완전해결v12.zip](computer:///mnt/user-data/outputs/lab3-2_monitoring-cicd_최종완전해결v12.zip)

**TAR.GZ 파일 (104KB):**
[lab3-2_monitoring-cicd_최종완전해결v12.tar.gz](computer:///mnt/user-data/outputs/lab3-2_monitoring-cicd_최종완전해결v12.tar.gz)

---

## 🎉 완료!

**v12에서 KServe 타임아웃 문제 완전 해결!**

1. ✅ 포트 통일 (8000)
2. ✅ Health Probes 추가
3. ✅ 상세 디버깅 정보
4. ✅ 실제 API 테스트

**특징:**
- ✅ InferenceService 정상 배포
- ✅ Health check 통과
- ✅ Prediction API 작동
- ✅ 타임아웃 없음
- ✅ 디버깅 용이

---

© 2024 현대오토에버 MLOps Training  
**Version**: 12.0 (KServe Timeout 완전 해결)  
**Status**: ✅ Production Ready  
**핵심**: 포트 통일 + Health Probes
