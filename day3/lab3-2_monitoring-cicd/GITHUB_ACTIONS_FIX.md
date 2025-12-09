# 🚨 GitHub Actions 의존성 충돌 완전 해결 가이드

## ❌ 문제 상황

GitHub Actions에서 2가지 의존성 충돌 발생:

**충돌 1: kubernetes 버전**
```
ERROR: Cannot install kfp 1.8.22 and kubernetes==28.1.0
The conflict is caused by:
    The user requested kubernetes==28.1.0
    kfp 1.8.22 depends on kubernetes<26 and >=8.0.0
```

**충돌 2: pydantic 버전**
```
ERROR: Cannot install pydantic==2.5.2 and kfp==1.8.22
The conflict is caused by:
    The user requested pydantic==2.5.2
    kfp 1.8.22 depends on pydantic<2 and >=1.8.2
```

## 🔍 근본 원인

**GitHub 저장소의 requirements.txt가 로컬 파일과 다릅니다!**

```
로컬 파일 (lab3-2 압축파일):
├── requirements.txt  ✅ kubernetes==25.3.0, pydantic==1.10.13

GitHub 저장소:
├── requirements.txt  ❌ kubernetes==28.1.0, pydantic==2.5.2  ← 문제!
```

## ✅ 해결 방법

### 방법 1: GitHub 저장소의 requirements.txt 직접 수정 (추천)

**1. GitHub 저장소 접속:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO
```

**2. requirements.txt 파일 찾기:**
```
.github/workflows/ 또는 루트 디렉토리
```

**3. requirements.txt 전체 내용을 아래로 교체:**

```txt
# Lab 3-2: Monitoring & CI/CD Requirements
# Compatible with Python 3.9-3.12

# Kubeflow Pipelines (requires kubernetes<26, pydantic<2)
kfp==1.8.22

# MLflow
mlflow==2.9.2

# Data Science (Python 3.12 compatible)
scikit-learn==1.4.0
pandas==2.1.4
numpy==1.26.4
joblib==1.3.2

# Model Serving (pydantic 1.x for kfp compatibility)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==1.10.13

# HTTP
httpx==0.25.2
requests==2.31.0

# Kubernetes (compatible with kfp 1.8.22)
kubernetes==25.3.0

# AWS
boto3==1.34.0
botocore==1.34.0

# Visualization
matplotlib==3.8.2
seaborn==0.13.0

# Utilities
python-dotenv==1.0.0
PyYAML==6.0.1

# Prometheus Client
prometheus-client==0.19.0

# CLI
click==8.1.7

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Build tools (for Python 3.12 compatibility)
setuptools>=65.0.0
```

**4. Commit & Push:**
```bash
git add requirements.txt
git commit -m "Fix: Update kubernetes to 25.3.0 for kfp 1.8.22 compatibility"
git push
```

**5. GitHub Actions 재실행:**
- Actions 탭 → 실패한 workflow → Re-run failed jobs

---

### 방법 2: .github/workflows/ci.yml 수정

**requirements.txt를 수정할 수 없다면**, workflow 파일에서 직접 의존성 지정:

```yaml
# .github/workflows/ci.yml
name: Test and Validate Model

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          # 명시적으로 호환 버전 설치
          pip install kfp==1.8.22
          pip install kubernetes==25.3.0
          pip install pydantic==1.10.13
          pip install mlflow==2.9.2
          pip install scikit-learn==1.3.2
          pip install pandas==2.0.3
          pip install numpy==1.24.3
          pip install pytest==7.4.3
          pip install pytest-cov==4.1.0
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=.
```

---

### 방법 3: 별도의 requirements-ci.txt 생성 (가장 안전)

**1. GitHub 저장소에 새 파일 생성:**

```bash
# requirements-ci.txt
kfp==1.8.22
kubernetes==25.3.0
pydantic==1.10.13
mlflow==2.9.2
scikit-learn==1.3.2
pandas==2.0.3
numpy==1.24.3
pytest==7.4.3
pytest-cov==4.1.0
```

**2. workflow 파일 수정:**

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements-ci.txt
```

---

## 🎯 검증 방법

### 로컬에서 먼저 테스트:

```bash
# 1. 가상환경 생성
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 2. requirements.txt 설치
pip install -r requirements.txt

# 3. 충돌 확인
pip list | grep -E "kfp|kubernetes"

# 예상 출력:
# kfp                    1.8.22
# kubernetes             25.3.0
# pydantic               1.10.13
```

---

## ✅ 성공 확인

**GitHub Actions 로그에서 확인:**

```
Run python -m pip install --upgrade pip
✅ Successfully installed kfp-1.8.22
✅ Successfully installed kubernetes-25.3.0
✅ Successfully installed pydantic-1.10.13
✅ Successfully installed mlflow-2.9.2
...
✅ All tests passed
```

---

## 📋 체크리스트

- [ ] GitHub 저장소의 requirements.txt 확인
- [ ] `kubernetes==25.3.0` 으로 수정
- [ ] `kfp==1.8.22` 확인
- [ ] Commit & Push
- [ ] GitHub Actions 재실행
- [ ] ✅ Install dependencies 성공
- [ ] ✅ All tests passed

---

## 🔧 문제가 계속된다면

### 캐시 문제일 수 있습니다:

```yaml
# .github/workflows/ci.yml에 추가
- name: Clear pip cache
  run: |
    pip cache purge
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

### 또는 dependency 고정:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --no-cache-dir -r requirements.txt
```

---

## 🎓 핵심 포인트

1. **로컬 파일 != GitHub 저장소 파일**
   - 로컬에서 수정해도 GitHub는 변경되지 않음
   - 반드시 GitHub 저장소에서 직접 수정

2. **kfp 1.8.22의 의존성 제약**
   - kubernetes<26 필수
   - pydantic<2 필수 (매우 중요!)
   - 두 가지 모두 충족해야 설치 가능

3. **버전 호환성**
   ```
   kfp 1.8.22  →  kubernetes<26, pydantic<2  ✅
   kfp 2.15.2  →  kubernetes>=28, pydantic>=2  ✅
   ```

4. **명확한 버전 지정이 중요**
   ```
   ❌ kubernetes>=25.0.0, pydantic>=1.0.0
   ✅ kubernetes==25.3.0, pydantic==1.10.13
   ```

---

## 📞 여전히 문제가 있다면

### 1. GitHub Actions 로그 전체 확인
```
Actions → 실패한 workflow → Job → Install dependencies
```

### 2. requirements.txt 내용 확인
```bash
# GitHub 저장소에서
cat requirements.txt | grep kubernetes

# 출력 확인:
kubernetes==25.3.0  ✅
kubernetes==28.1.0  ❌
```

### 3. 캐시 삭제 후 재시도
```
Actions → 해당 workflow → ... → Delete workflow cache
```

---

© 2024 현대오토에버 MLOps Training  
**Version**: GitHub Actions 완전 해결판  
**Status**: 명확한 수정 가이드 제공
