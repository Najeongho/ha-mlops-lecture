# Lab 1-4: Hello World Pipeline

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 40분 |
| **난이도** | ⭐⭐ |
| **목표** | Kubeflow Pipeline SDK로 첫 파이프라인 작성 및 실행 |

## 🎯 학습 목표

- KFP SDK로 컴포넌트 정의
- 파이프라인 구성 및 컴파일
- Kubeflow UI에서 파이프라인 실행
- 실행 결과 및 로그 확인

## 🏗️ 파이프라인 구조

```
┌─────────┐     ┌──────────┐     ┌──────────────┐
│   add   │ ──▶ │ multiply │ ──▶ │ print_result │
│ (a + b) │     │  (x * 2) │     │   (출력)     │
└─────────┘     └──────────┘     └──────────────┘
   ▲   ▲             │
   │   │             │
  a=3 b=5        sum=8 ──▶ product=16
```

## 📁 파일 구조

```
lab1-4_hello-pipeline/
├── README.md                    # 이 파일
├── hello_pipeline.py            # 파이프라인 코드
├── hello_pipeline.ipynb         # Jupyter Notebook 버전
└── run_pipeline.py              # 파이프라인 실행 스크립트
```

## 🔧 실습 단계

### Step 1: 파이프라인 코드 작성

`hello_pipeline.py` 파일 참조 또는 Notebook에서 작성

### Step 2: 파이프라인 컴파일

```python
from kfp import compiler

compiler.Compiler().compile(
    pipeline_func=hello_pipeline,
    package_path='hello_pipeline.yaml'
)
```

### Step 3: 파이프라인 실행

```python
import kfp

client = kfp.Client()
run = client.create_run_from_pipeline_func(
    hello_pipeline,
    arguments={'a': 10, 'b': 20, 'factor': 3},
    experiment_name='hello-experiment'
)
print(f"Run ID: {run.run_id}")
```

### Step 4: 결과 확인

1. Kubeflow Dashboard → **Runs** 메뉴
2. 실행 선택 → **Graph** 탭에서 DAG 확인
3. 각 컴포넌트 클릭 → **Logs** 탭에서 출력 확인

## ✅ 완료 체크리스트

- [ ] 3개 컴포넌트 정의 (add, multiply, print_result)
- [ ] 파이프라인 함수 정의
- [ ] YAML 파일 컴파일 성공
- [ ] 파이프라인 실행 (Status: Succeeded)
- [ ] 로그에서 결과 확인

## 🧪 테스트 케이스

| a | b | factor | 예상 결과 |
|---|---|--------|----------|
| 3 | 5 | 2 | 16 |
| 10 | 20 | 3 | 90 |
| 7 | 3 | 5 | 50 |

## ❓ 트러블슈팅

### 문제: "ModuleNotFoundError: No module named 'kfp'"

```python
!pip install kfp==1.8.22
```

### 문제: Pipeline 상태가 "Pending"

```bash
# Pod 상태 확인
kubectl get pods -n kubeflow-userXX

# 이벤트 확인
kubectl describe pod [pod-name] -n kubeflow-userXX
```

### 문제: "Forbidden" 에러

네임스페이스 권한 확인:
```bash
kubectl auth can-i create pods -n kubeflow-userXX
```

## 📚 참고 자료

- [Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/components/pipelines/sdk/)
- [KFP Component 작성법](https://www.kubeflow.org/docs/components/pipelines/sdk/component-development/)
