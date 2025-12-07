# Lab 1-3: Jupyter Notebook 설정

## 📋 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 20분 |
| **난이도** | ⭐ |
| **목표** | Kubeflow Notebook 서버 생성 및 환경 구성 |

## 🎯 학습 목표

- Kubeflow Notebook 서버 생성
- JupyterLab 인터페이스 탐색
- Python 환경 및 KFP SDK 설치 확인

## 🔧 실습 단계

### Step 1: Notebook 서버 생성

1. Kubeflow Dashboard → **Notebooks** 클릭
2. **+ New Notebook** 버튼 클릭
3. 설정 입력:

| 설정 | 값 |
|------|-----|
| Name | `notebook-userXX` |
| Image | `jupyter-scipy:v1.7.0` |
| CPU | `1` |
| Memory | `2Gi` |
| GPU | `None` |
| Workspace Volume | `10Gi` |

4. **LAUNCH** 버튼 클릭
5. Status가 **Running**이 될 때까지 대기 (2-3분)
6. **CONNECT** 버튼 클릭

### Step 2: JupyterLab 환경 확인

새 Notebook 파일을 생성하고 다음 코드 실행:

```python
# Cell 1: Python 버전 확인
import sys
print(f"Python Version: {sys.version}")
```

```python
# Cell 2: 주요 패키지 확인
import numpy as np
import pandas as pd
import sklearn

print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
```

```python
# Cell 3: Kubernetes 환경 확인
import os

print(f"Hostname: {os.getenv('HOSTNAME', 'N/A')}")
print(f"Home Directory: {os.getenv('HOME', 'N/A')}")
```

### Step 3: KFP SDK 설치

Terminal 또는 Notebook에서 실행:

```bash
pip install kfp==1.8.22
```

설치 확인:

```python
# Cell 4: KFP SDK 확인
import kfp
from kfp import dsl
from kfp.components import create_component_from_func

print(f"KFP Version: {kfp.__version__}")
print("✅ KFP SDK installed successfully!")
```

### Step 4: 추가 패키지 설치 (선택)

```bash
# MLflow 설치
pip install mlflow==2.9.2

# 기타 유용한 패키지
pip install matplotlib seaborn
```

## ✅ 완료 체크리스트

- [ ] Notebook 서버 생성 (Status: Running)
- [ ] JupyterLab 접속 성공
- [ ] Python 환경 확인
- [ ] KFP SDK 설치 완료

## 📁 Notebook 파일 구조

```
/home/jovyan/
├── work/           # 작업 디렉토리 (권장)
│   ├── day1/
│   ├── day2/
│   └── day3/
└── .local/         # pip 설치 패키지
```

## ❓ 트러블슈팅

### 문제: Notebook 생성 시 "Pending" 상태 지속

```bash
# Pod 상태 확인
kubectl get pods -n kubeflow-userXX

# 이벤트 확인
kubectl describe pod notebook-userXX-0 -n kubeflow-userXX
```

### 문제: "ModuleNotFoundError"

```python
# 패키지 재설치
!pip install --upgrade [패키지명]

# Kernel 재시작
# Kernel → Restart Kernel
```

## 📚 참고 자료

- [Kubeflow Notebooks](https://www.kubeflow.org/docs/components/notebooks/)
- [JupyterLab 문서](https://jupyterlab.readthedocs.io/)
