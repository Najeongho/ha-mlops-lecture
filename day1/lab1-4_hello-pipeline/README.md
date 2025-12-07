# Lab 1-4: Hello World Pipeline

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 40분 |
| **난이도** | ⭐⭐ |
| **목표** | KFP SDK v2로 첫 번째 Kubeflow Pipeline 작성 및 실행 |

## 🎯 학습 목표

- KFP SDK v2로 컴포넌트 정의하기
- 여러 컴포넌트로 파이프라인 구성하기
- 파이프라인을 YAML로 컴파일하기
- Kubeflow UI를 통해 파이프라인 업로드 및 실행하기
- 실행 결과 및 로그 확인하기

## 🏗️ 파이프라인 구조

```
┌─────────┐     ┌──────────┐     ┌──────────────┐
│   add   │ ──▶ │ multiply │ ──▶ │ print_result │
│ (a + b) │     │  (x * f) │     │   (출력)     │
└─────────┘     └──────────┘     └──────────────┘
   ▲   ▲             │
   │   │             │
  a=3 b=5        sum=8 ──▶ product=16
```

**계산식:** `(a + b) * factor`

**예시:** `(10 + 20) * 3 = 90`

## 📁 파일 구조

```
lab1-4_hello-pipeline/
├── README.md                    # 이 파일
├── hello_pipeline.py            # 파이프라인 Python 스크립트
├── hello_pipeline.ipynb         # Jupyter Notebook 버전
└── requirements.txt             # Python 패키지 의존성
```

## 🔧 사전 요구사항

### 필수 소프트웨어
- Python 3.11+
- Kubeflow Pipelines (클러스터에 설치됨)
- Jupyter Notebook (.ipynb 버전 사용 시)

### 필수 Python 패키지
```bash
pip install kfp
```

또는

```bash
pip install -r requirements.txt
```

## 📚 실습 단계

### 방법 1: Jupyter Notebook 사용 (권장)

1. **Kubeflow Jupyter에 Notebook 업로드**
   ```bash
   # Kubeflow Jupyter 환경에서
   파일 업로드: hello_pipeline.ipynb
   ```

2. **모든 셀 실행**
   - 순서대로 셀 실행
   - YAML 파일 `hello_pipeline_en.yaml` 생성됨

3. **Kubeflow UI에 파이프라인 업로드**
   - `hello_pipeline_en.yaml` 다운로드
   - Kubeflow Dashboard → Pipelines → Upload pipeline
   - 파일 업로드

4. **Run 생성 및 실행**
   - Parameters 설정: a=10, b=20, factor=3
   - Graph 및 Logs 탭에서 결과 확인

### 방법 2: Python 스크립트 사용

1. **스크립트 실행**
   ```bash
   python hello_pipeline.py
   ```

2. **출력**
   - `hello_pipeline_en.yaml` 생성됨

3. **Kubeflow에 업로드**
   - 방법 1과 동일한 단계로 진행

## 🔍 파이프라인 컴포넌트

### Component 1: add
```python
@dsl.component(base_image='python:3.11')
def add(a: int, b: int) -> int:
    result = a + b
    print(f"Add: {a} + {b} = {result}")
    return result
```

**목적:** 두 숫자를 더합니다

### Component 2: multiply
```python
@dsl.component(base_image='python:3.11')
def multiply(x: int, factor: int = 2) -> int:
    result = x * factor
    print(f"Multiply: {x} * {factor} = {result}")
    return result
```

**목적:** 숫자에 factor를 곱합니다

### Component 3: print_result
```python
@dsl.component(base_image='python:3.11')
def print_result(value: int):
    print("=" * 50)
    print(f"Final Result: {value}")
    print("=" * 50)
```

**목적:** 최종 결과를 출력합니다

## 🧪 테스트 케이스

| a | b | factor | 예상 결과 |
|---|---|--------|----------|
| 3 | 5 | 2 | 16 |
| 10 | 20 | 3 | 90 |
| 7 | 3 | 5 | 50 |
| 100 | 200 | 2 | 600 |

## ✅ 예상 출력

### add 컴포넌트
```
Add: 10 + 20 = 30
```

### multiply 컴포넌트
```
Multiply: 30 * 3 = 90
```

### print_result 컴포넌트
```
==================================================
Final Result: 90
==================================================
```

## ❓ 트러블슈팅

### 문제: "ModuleNotFoundError: No module named 'kfp'"

**해결방법:**
```bash
pip install kfp
```

### 문제: Pipeline 상태가 "Pending"으로 유지됨

**해결방법:**
```bash
# Pod 상태 확인
kubectl get pods -n kubeflow-user-example

# 이벤트 확인
kubectl describe pod [pod-name] -n kubeflow-user-example
```

### 문제: "Forbidden" 에러 발생

**해결방법:**
- 네임스페이스 권한 확인
```bash
kubectl auth can-i create pods -n kubeflow-user-example
```

### 문제: UTF-8 Collation 에러

**해결방법:**
- 모든 description과 텍스트를 영어로만 작성
- Pipeline/Component 이름에 특수문자나 이모지 사용 금지
- 한글이나 다른 non-ASCII 문자 사용 금지

## ✅ 완료 체크리스트

- [ ] 3개 컴포넌트 정의 (add, multiply, print_result)
- [ ] 파이프라인 함수 정의
- [ ] YAML 파일 컴파일 성공
- [ ] Kubeflow에 파이프라인 업로드
- [ ] Run 실행 성공 (Status: Succeeded)
- [ ] 로그에서 결과 확인

## 📖 핵심 개념

### Component
파이프라인의 한 단계를 수행하는 독립적인 코드 조각입니다. KFP v2에서는 `@dsl.component` 데코레이터로 정의합니다.

### Pipeline
여러 컴포넌트가 연결된 워크플로우입니다. `@dsl.pipeline` 데코레이터로 정의합니다.

### DAG (Directed Acyclic Graph)
파이프라인의 실행 흐름을 나타내며, 컴포넌트 간의 의존성을 보여줍니다.

### Experiment
Run을 논리적으로 그룹화하여 조직하고 비교하는 단위입니다.

### Run
특정 파라미터 값으로 파이프라인을 한 번 실행하는 것입니다.

## 🔑 KFP v2 주요 기능

### 컴포넌트 정의
```python
@dsl.component(base_image='python:3.11')
def my_component(arg: type) -> type:
    # 컴포넌트 로직
    return result
```

### 파이프라인 정의
```python
@dsl.pipeline(name='My Pipeline', description='Description')
def my_pipeline(param: type):
    task1 = component1(arg=param)
    task2 = component2(arg=task1.output)
```

### 컴파일
```python
from kfp import compiler
compiler.Compiler().compile(
    pipeline_func=my_pipeline,
    package_path='pipeline.yaml'
)
```

## 📚 참고 자료

- [Kubeflow Pipelines 문서](https://www.kubeflow.org/docs/components/pipelines/)
- [KFP SDK v2 문서](https://kubeflow-pipelines.readthedocs.io/)
- [KFP Component 개발 가이드](https://www.kubeflow.org/docs/components/pipelines/v2/components/)

## 🚀 다음 단계

- **Day 2:** 모델 서빙 (FastAPI, MLflow, KServe)
- **Day 3:** End-to-End ML Pipeline

## 📝 주의사항

### 중요 설정

1. **KFP 버전:** 이 실습은 KFP v2 (최신 버전)를 사용합니다.

2. **Base Image:** 모든 컴포넌트는 `python:3.11`을 base image로 사용합니다.

3. **텍스트 인코딩:** Kubeflow 백엔드 데이터베이스의 UTF-8 collation 문제를 피하기 위해 코드 내 모든 텍스트(description, print 등)는 영어만 사용하세요.

4. **인증:** 인증 설정으로 인해 Jupyter에서 직접 실행하는 대신 UI를 통한 업로드 방식을 사용합니다.

### 모범 사례

- 컴포넌트 함수는 단순하고 집중적으로 작성
- 모든 파라미터와 반환 값에 타입 힌트 사용
- 컴포넌트와 파이프라인에 docstring 포함
- 의미있는 변수 이름 사용
- 파이프라인 실행 전 컴포넌트를 로컬에서 테스트
- 모든 이름과 description은 영어로 작성
