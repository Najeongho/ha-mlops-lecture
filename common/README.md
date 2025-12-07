# Common Utilities

이 디렉토리는 MLOps 교육에서 사용하는 공통 유틸리티 스크립트를 포함합니다.

## 📁 파일 목록

| 파일 | 설명 |
|------|------|
| `check-status.sh` | 환경 상태 확인 스크립트 |
| `cleanup.sh` | 실습 환경 정리 스크립트 |

## 🔧 사용 방법

### 환경 상태 확인

현재 네임스페이스의 모든 리소스 상태를 확인합니다.

```bash
# 기본 사용
./check-status.sh

# 특정 네임스페이스 지정
./check-status.sh kubeflow-user01

# 환경 변수로 지정
export NAMESPACE=kubeflow-user01
./check-status.sh
```

**확인 항목:**
- Kubernetes 연결 상태
- Namespace 존재 여부
- Pods 상태 (Running/Pending/Failed)
- Deployments 상태
- Services 목록
- InferenceServices (KServe)
- Kubeflow Pipelines 상태
- MLflow 서버 상태
- 리소스 사용량
- 최근 이벤트

### 환경 정리

실습 후 생성된 리소스를 정리합니다.

```bash
# 기본 사용 (확인 후 삭제)
./cleanup.sh

# 특정 네임스페이스 지정
./cleanup.sh kubeflow-user01
```

**정리 항목:**
- InferenceServices
- Deployments (교육용)
- Services (교육용)
- ConfigMaps (교육용)
- Secrets (교육용)
- Completed/Failed Pods

**⚠️ 주의:** PVC는 데이터 손실 방지를 위해 자동 삭제하지 않습니다.

## 💡 권한 설정

스크립트 실행 전 실행 권한을 부여하세요:

```bash
chmod +x check-status.sh cleanup.sh
```

## 📝 요구 사항

- kubectl이 설치되어 있어야 합니다.
- Kubernetes 클러스터에 접근 가능해야 합니다.
- 해당 네임스페이스에 대한 권한이 필요합니다.
