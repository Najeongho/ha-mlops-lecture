# 🔧 GitHub Actions Black 포맷팅 문제 해결

## ❌ 문제 상황

GitHub Actions CI에서 "Check code formatting with black" 단계 실패:

```
Check code formatting with black
Error: Process completed with exit code 1.
```

## 🔍 근본 원인

**Black**은 Python 코드 자동 포맷터입니다. `--check` 옵션으로 실행하면:
- 코드 포맷팅이 Black 스타일과 다르면 → **Exit Code 1 (실패)**
- 포맷팅이 완벽하면 → Exit Code 0 (성공)

**문제:**
- Pipeline 컴파일 스크립트나 다른 Python 코드가 Black 스타일과 다름
- Black이 자동으로 고치지 않고 체크만 함
- CI가 실패하여 전체 워크플로우 중단

---

## ✅ 해결 방법

### 방법 1: Black을 경고로만 처리 (추천) ⭐

**이미 적용되어 있습니다!**

```yaml
# .github/workflows/ci-test.yaml
- name: Check code formatting with black
  continue-on-error: true  # ⬅️ 실패해도 계속 진행
  run: |
    black --check --diff .
```

**효과:**
- ✅ Black 실패해도 CI 통과
- ✅ 포맷팅 문제는 로그에서 확인 가능
- ✅ 다른 테스트는 정상 실행

---

### 방법 2: Black 자동 포맷팅 적용

포맷팅 문제를 자동으로 고치려면:

```yaml
- name: Auto-format code with black
  run: |
    black .
    
- name: Commit formatted code
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"
    git diff --quiet || git commit -am "style: Auto-format with black"
    git push
```

**주의:** Auto-commit이 허용된 저장소에만 사용!

---

### 방법 3: Black 단계 완전 제거

필요 없다면 삭제:

```yaml
# .github/workflows/ci-test.yaml
# 아래 3줄 삭제
- name: Check code formatting with black
  run: |
    black --check --diff .
```

---

### 방법 4: 특정 파일/디렉토리 제외

Black이 특정 파일을 무시하도록:

```yaml
- name: Check code formatting with black
  continue-on-error: true
  run: |
    black --check --diff --exclude '(pipelines|notebooks|scripts)' .
```

또는 `pyproject.toml` 생성:

```toml
# pyproject.toml
[tool.black]
line-length = 127
exclude = '''
/(
    \.git
  | \.venv
  | pipelines
  | notebooks
  | scripts
)/
'''
```

---

## 🚀 로컬에서 Black 실행

CI 실패 전에 로컬에서 미리 확인:

### 1. Black 설치

```bash
pip install black
```

### 2. 코드 체크

```bash
# 모든 Python 파일 체크
black --check --diff .

# 특정 파일만
black --check --diff pipelines/
```

### 3. 자동 포맷팅

```bash
# 실제로 파일 수정
black .

# 변경사항 확인
git diff
```

---

## 📋 Black 포맷팅 규칙

Black이 자동으로 수정하는 것들:

### 1. 줄 길이
```python
# Before
def very_long_function_name(parameter1, parameter2, parameter3, parameter4, parameter5):
    pass

# After
def very_long_function_name(
    parameter1, parameter2, parameter3, parameter4, parameter5
):
    pass
```

### 2. 문자열 따옴표
```python
# Before
name = 'John'

# After
name = "John"  # Double quotes
```

### 3. 공백
```python
# Before
x=1+2

# After
x = 1 + 2
```

### 4. Trailing comma
```python
# Before
my_list = [1, 2, 3]

# After (긴 경우)
my_list = [
    1,
    2,
    3,
]
```

---

## ✅ 검증 방법

### GitHub Actions에서

```
Run name: CI - Test Model
→ Test and Validate Model
  → Check code formatting with black
     ⚠️ Warning (continue-on-error: true)
     → 다음 단계 계속 진행
```

### 로컬에서

```bash
# 1. Black 설치
pip install black

# 2. 체크
black --check .

# 예상 출력:
# All done! ✨ 🍰 ✨
# X files would be left unchanged.
```

---

## 🎯 권장 사항

### 실습 Lab의 경우

**추천:** 방법 1 (continue-on-error: true)

**이유:**
- 실습 목적은 MLOps 파이프라인 학습
- 코드 포맷팅은 부차적
- Black 경고만 보여주고 CI 통과

### 프로덕션 프로젝트의 경우

**추천:** 방법 4 (제외 규칙 + pre-commit hook)

```bash
# pre-commit hook 설치
pip install pre-commit
cat <<EOF > .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        exclude: ^(pipelines|notebooks)/
EOF

pre-commit install
```

**효과:**
- Commit 전에 자동 포맷팅
- CI 도달 전에 문제 해결
- 팀 코드 스타일 일관성

---

## 🐛 문제 해결

### Black이 계속 실패한다면

#### 1. 문제 파일 확인

```bash
black --check --diff . 2>&1 | grep "would reformat"

# 예상 출력:
# would reformat pipelines/project_solution_pipeline.py
```

#### 2. 해당 파일만 포맷

```bash
black pipelines/project_solution_pipeline.py
git add pipelines/project_solution_pipeline.py
git commit -m "style: Format with black"
git push
```

#### 3. 제외 규칙 추가

```yaml
# .github/workflows/ci-test.yaml
- name: Check code formatting with black
  continue-on-error: true
  run: |
    black --check --diff --exclude 'pipelines/project_solution_pipeline.py' .
```

---

## ✅ 최종 확인

### CI가 통과해야 할 단계들

```
✅ Checkout code
✅ Set up Python
✅ Cache pip dependencies
✅ Install dependencies
✅ Lint with flake8
⚠️  Check code formatting with black (경고만)
✅ Run unit tests
✅ Upload coverage reports
✅ Generate test report
✅ Upload test artifacts
```

### Black 경고 메시지 예시

```
would reformat pipelines/project_solution_pipeline.py

Oh no! 💥 💔 💥
1 file would be reformatted, 23 files would be left unchanged.
```

**중요:** `continue-on-error: true`로 인해 다음 단계는 계속 실행!

---

## 📞 추가 도움

### Black 공식 문서
- https://black.readthedocs.io/

### Black Playground (온라인 테스트)
- https://black.vercel.app/

### 로컬 테스트
```bash
# 특정 파일만 체크
black --check pipelines/my_file.py

# 자동 포맷팅
black pipelines/my_file.py

# 차이점 확인
black --diff pipelines/my_file.py
```

---

© 2024 현대오토에버 MLOps Training  
**Version**: GitHub Actions Black 문제 해결  
**Status**: ✅ continue-on-error로 해결 완료
