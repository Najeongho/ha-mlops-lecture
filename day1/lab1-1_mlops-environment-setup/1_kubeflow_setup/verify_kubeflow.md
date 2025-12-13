# Kubeflow Tenant 검증 스크립트 사용 가이드

## 📋 개요

이 스크립트는 수강생 본인의 Kubeflow 환경이 올바르게 설정되었는지 자동으로 검증합니다.

## 🚀 빠른 시작

### 1. 스크립트 실행 권한 부여

```bash
chmod +x verify_kubeflow.sh
```

### 2. 사용자 번호 설정 및 실행

```bash
# 방법 1: 환경 변수 설정 후 실행
export USER_NUM="07"  # 본인의 번호로 변경
./verify_kubeflow.sh

# 방법 2: 실행 시 입력
./verify_kubeflow.sh
# 사용자 번호를 입력하세요: 07
```

## 📊 검증 항목

이 스크립트는 다음 10가지 항목을 검증합니다:

### Step 1: Namespace 존재 및 이름 확인
- Namespace가 `kubeflow-userXX` 형식으로 존재하는지 확인
- 생성 날짜 및 레이블 확인

### Step 2: Profile 존재 및 이름 일치 확인
- Profile이 존재하는지 확인
- **중요**: Profile 이름과 Namespace 이름이 일치하는지 확인
- Profile Ready 상태 확인
- Owner 정보 확인

### Step 3: ServiceAccount 확인
- `default-editor` ServiceAccount 존재 확인
- `default-viewer` ServiceAccount 존재 확인
- 이 항목이 없으면 Jupyter Notebook 생성 불가

### Step 4: ResourceQuota 확인
- CPU, Memory 할당량 확인
- 현재 사용률 확인

### Step 5: RoleBinding 확인
- 사용자 권한 설정 확인
- `namespaceAdmin` 등 필수 권한 확인

### Step 6: PodDefault 확인
- MLflow 접근 설정 확인
- Kubeflow Pipelines 접근 설정 확인

### Step 7: 네임스페이스 내 리소스 확인
- Pods, Services, PVC 등 현재 리소스 상태 확인

### Step 8: 권한 격리 테스트
- 다른 사용자의 Namespace에 접근 불가능한지 확인

### Step 9: Kubeflow 주요 컴포넌트 확인
- Central Dashboard, Pipelines UI, Notebook Controller 상태 확인

### Step 10: 실습 가능 여부 최종 판단
- 필수 요구사항 충족 여부 확인
- 실습 진행 가능 여부 판단

---

## ✅ 성공 예시

```
============================================================
검증 결과 요약
============================================================

  ✅ 통과: 8
  ❌ 실패: 0
  ⚠️  경고: 2
  📊 총점: 8/10

✅ 필수 검증을 모두 통과했습니다!

⚠️  일부 경고 사항이 있지만 실습 진행에는 문제없습니다.
다음 단계: Lab 1-1 Part 2 (Jupyter Notebook 생성)로 진행하세요.
```

**실습 가능 조건:**
- ✅ Namespace 존재
- ✅ ServiceAccount 생성 (최소 1개)
- ✅ RoleBinding 설정
- ✅ Kubeflow 시스템 정상

---

## ⚠️ 일반적인 문제 및 해결 방법

### 문제 1: Profile이 "Not Ready" 상태

**증상:**
```
상태: NO STATUS (Profile Controller가 처리 중)
```

**해결 방법:**
1. 정상적인 현상입니다. Profile Controller가 처리 중입니다.
2. ServiceAccount와 RoleBinding이 생성되면 실습 가능합니다.
3. 5분 후 다시 스크립트를 실행해보세요.

**언제 문제인가?**
- 30분 이상 지나도 Ready가 안 될 때 → 강사 문의

---

### 문제 2: ServiceAccount가 없음

**증상:**
```
❌ ServiceAccount를 찾을 수 없습니다: default-editor
❌ ServiceAccount를 찾을 수 없습니다: default-viewer
```

**원인:**
1. Profile이 Ready 상태가 아님
2. Profile Controller가 아직 처리 중
3. Profile과 Namespace 이름 불일치

**해결 방법:**
1. 위의 Profile 상태를 확인
2. 5분 후 다시 스크립트 실행
3. 계속 실패하면 강사에게 다음 정보 전달:
   - Profile: kubeflow-userXX
   - Namespace: kubeflow-userXX
   - Profile Status 결과

---

### 문제 3: RoleBinding이 없음

**증상:**
```
❌ RoleBinding을 찾을 수 없습니다.
```

**해결 방법:**
1. ServiceAccount가 먼저 생성되어야 함
2. Profile이 Ready 상태가 되면 자동 생성
3. 강사에게 RBAC 설정 문의

---

### 문제 4: Profile과 Namespace 이름 불일치

**증상:**
```
❌ Profile과 Namespace 이름이 일치하지 않습니다!
   Profile: profile-user07
   Namespace: kubeflow-user07
```

**원인:**
- 구 버전 Profile 이름 형식 사용 중

**해결 방법:**
- 즉시 강사에게 알림 (Profile 재생성 필요)

---

## 🆘 강사 문의 시 제공할 정보

검증 실패 시 다음 정보를 강사에게 전달하세요:

```bash
# 1. 기본 정보
사용자 번호: XX
Namespace: kubeflow-userXX
Profile: kubeflow-userXX

# 2. 검증 결과
./verify_kubeflow.sh 실행 결과 전체 캡처

# 3. Profile 상세 정보
kubectl get profile kubeflow-userXX -o yaml

# 4. 이벤트 로그
kubectl get events -n kubeflow-userXX --sort-by='.lastTimestamp'
```

---

## 📌 유용한 추가 명령어

### Profile 상세 확인
```bash
kubectl get profile kubeflow-user07 -o yaml
```

### Namespace 모든 리소스 확인
```bash
kubectl get all -n kubeflow-user07
```

### 이벤트 로그 확인 (문제 진단)
```bash
kubectl get events -n kubeflow-user07 --sort-by='.lastTimestamp'
```

### Kubeflow Dashboard 접속
```bash
# 포트 포워딩
kubectl port-forward svc/centraldashboard -n kubeflow 8080:80

# 브라우저에서 접속
# http://localhost:8080
```

### ServiceAccount 수동 확인
```bash
kubectl get sa -n kubeflow-user07
```

### RoleBinding 수동 확인
```bash
kubectl get rolebinding -n kubeflow-user07
```

---

## 🔍 검증 결과 해석

### 통과 점수별 의미

| 점수 | 의미 | 조치 |
|------|------|------|
| 9~10/10 | 완벽 | 즉시 실습 시작 |
| 7~8/10 | 양호 | 실습 가능, 일부 경고 확인 |
| 5~6/10 | 주의 | 실습 가능하나 문제 해결 권장 |
| 0~4/10 | 불가 | 강사 문의 필수 |

### 실습 가능 여부

**✅ 실습 가능 조건:**
```
✓ Namespace 존재
✓ ServiceAccount 생성됨 (1/2 이상)
✓ RoleBinding 설정됨
✓ Kubeflow 시스템 정상
```

**❌ 실습 불가 조건:**
```
✗ Namespace 없음
✗ ServiceAccount 없음
✗ RoleBinding 없음
✗ Kubeflow 시스템 문제
```

---

## 💡 자주 묻는 질문 (FAQ)

### Q1: Profile이 "Not Ready"인데 실습 가능한가요?

**A:** 네, 가능합니다!

Profile Status가 "Not Ready"여도 다음이 충족되면 실습 가능합니다:
- ServiceAccount 생성됨
- RoleBinding 설정됨
- Kubeflow 시스템 정상

Profile Controller가 처리 중일 수 있으며, 실습에는 영향 없습니다.

### Q2: 경고(⚠️)가 있는데 실습해도 되나요?

**A:** 대부분 괜찮습니다!

경고는 권장 사항이지 필수가 아닙니다. 예:
- PodDefault 없음 → 실습 가능하나 일부 기능 불편
- NetworkPolicy 없음 → 실습 가능하나 보안 권장 사항

필수 항목(✅/❌)만 확인하세요.

### Q3: 스크립트를 여러 번 실행해도 되나요?

**A:** 네, 문제없습니다!

이 스크립트는 읽기 전용으로 아무것도 변경하지 않습니다.
문제 해결 후 재검증 목적으로 여러 번 실행하세요.

### Q4: 검증 실패 후 어떻게 해야 하나요?

**A:** 다음 순서로 진행하세요:

1. **5분 대기** → Profile Controller 처리 시간
2. **재검증** → `./verify_kubeflow.sh` 다시 실행
3. **여전히 실패** → 강사 문의 (위의 정보 제공)

### Q5: 다른 사용자와 결과를 비교하고 싶어요

**A:** 다음 명령어로 비교하세요:

```bash
# 본인
export USER_NUM="07"
./verify_kubeflow.sh | grep "총점:"

# 다른 사용자 (참고용, 권한 있을 때만)
export USER_NUM="01"
./verify_kubeflow.sh | grep "총점:"
```

---

## 📚 관련 문서

- Lab 1-1 Part 2: Jupyter Notebook 생성
- Lab 1-2: Kubeflow Pipelines 기초
- MLOps 실습 가이드

---

## 🔧 트러블슈팅 체크리스트

검증 실패 시 순서대로 확인:

```bash
# 1. kubectl 명령어 작동 확인
kubectl get nodes

# 2. Kubeflow namespace 확인
kubectl get namespace kubeflow

# 3. 본인 Namespace 확인
kubectl get namespace kubeflow-user07

# 4. Profile 목록 확인
kubectl get profiles

# 5. Profile 상세 정보
kubectl get profile kubeflow-user07 -o yaml

# 6. 이벤트 로그 확인
kubectl get events -n kubeflow-user07

# 7. Profile Controller 상태
kubectl get pods -n kubeflow | grep profiles
```

---

## ⚙️ 스크립트 커스터마이징

### 환경 변수로 기본값 설정

```bash
# .bashrc 또는 .zshrc에 추가
export USER_NUM="07"
export KUBEFLOW_NAMESPACE="kubeflow-user07"

# 이후 스크립트 실행 시 자동 적용
./verify_kubeflow.sh
```

### 특정 단계만 실행 (고급)

스크립트를 수정하여 필요한 부분만 주석 해제하여 사용할 수 있습니다.

---

## 📞 지원

- **기술 문제**: 강사에게 문의
- **환경 설정**: 관리자에게 문의
- **스크립트 개선**: GitHub Issue 또는 강사 피드백

---

© 2025 현대오토에버 MLOps Training