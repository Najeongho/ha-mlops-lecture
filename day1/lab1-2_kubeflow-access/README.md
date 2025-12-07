# Lab 1-2: Kubeflow 대시보드 접속

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 15분 |
| **난이도** | ⭐ |
| **목표** | Kubeflow Central Dashboard 접속 및 UI 탐색 |

## 🎯 학습 목표

- kubectl port-forward를 통한 대시보드 접속
- Kubeflow UI 구성 이해
- 네임스페이스 선택 방법

## 🔧 실습 단계

### Step 1: 포트 포워딩 설정

```bash
kubectl port-forward svc/istio-ingressgateway \
    -n istio-system 8080:80
```

⚠️ **이 터미널은 열어둔 상태로 유지하세요!**

### Step 2: 브라우저에서 접속

브라우저에서 다음 URL로 접속:

```
http://localhost:8080
```

### Step 3: 로그인

```
Email: userXX@example.com (XX는 본인 번호)
Password: [제공된 비밀번호]
```

### Step 4: 네임스페이스 선택

1. 상단 헤더에서 네임스페이스 드롭다운 클릭
2. `kubeflow-userXX` 선택
3. 모든 작업은 자신의 네임스페이스에서 수행

### Step 5: 대시보드 탐색

좌측 메뉴에서 각 항목 확인:

| 메뉴 | 설명 |
|------|------|
| **Notebooks** | Jupyter Notebook 서버 관리 |
| **Volumes** | 스토리지 볼륨 관리 |
| **Pipelines** | ML 파이프라인 목록 |
| **Experiments** | 실험 관리 |
| **Runs** | 파이프라인 실행 기록 |

## ✅ 완료 체크리스트

- [ ] 포트 포워딩 실행
- [ ] 대시보드 로그인 성공
- [ ] 본인 네임스페이스 선택
- [ ] 각 메뉴 탐색 완료

## ❓ 트러블슈팅

### 문제: "Connection refused"

포트 포워딩이 실행 중인지 확인:

```bash
# 다른 터미널에서 확인
ps aux | grep port-forward
```

### 문제: "403 Forbidden"

네임스페이스 권한 확인:

```bash
kubectl auth can-i get pods -n kubeflow-userXX
```

## 📚 참고 자료

- [Kubeflow 공식 문서](https://www.kubeflow.org/docs/)
