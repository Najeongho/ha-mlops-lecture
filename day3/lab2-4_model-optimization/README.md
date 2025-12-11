# Lab 2-4 (Bonus): Model Optimization - ONNX 변환 및 경량화

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 40분 |
| **난이도** | ⭐⭐⭐ |
| **목표** | 학습된 ML 모델을 ONNX로 변환하고 추론 성능을 최적화 |
| **유형** | 🎁 **Bonus Lab** (선택적 실습) |

> ⚠️ **참고**: 이 Lab은 Day 2 정규 실습 이후 또는 자습 시간에 진행하는 선택적 실습입니다.

## 🎯 학습 목표

이 실습을 통해 다음을 학습합니다:
- **ONNX 포맷** 이해 및 변환 방법
- **모델 경량화** 기법 개요 (Quantization, Pruning)
- **추론 성능 비교** (원본 vs ONNX vs 양자화)
- **MLflow**에 최적화된 모델 등록
- **KServe**에서 ONNX 모델 서빙

---

## 🏗️ 실습 구조

```
Lab 2-4 (Bonus): Model Optimization (40분)
│
├── Part 1: ONNX 변환 (15분)
│   ├── Scikit-learn 모델 → ONNX
│   ├── PyTorch 모델 → ONNX (선택)
│   └── ONNX 모델 검증
│
├── Part 2: 양자화 적용 (10분)
│   ├── 동적 양자화 (Dynamic Quantization)
│   ├── 모델 크기 비교
│   └── 정확도 비교
│
└── Part 3: 성능 벤치마크 (15분)
    ├── 추론 시간 측정
    ├── MLflow에 메트릭 기록
    └── 결과 분석
```

---

## 📁 파일 구조

```
lab2-4_model-optimization/
├── README.md                         # ⭐ 이 파일 (실습 가이드)
├── requirements.txt                  # Python 패키지
├── scripts/
│   ├── 1_onnx_conversion.py         # Part 1: ONNX 변환
│   ├── 2_quantization.py            # Part 2: 양자화
│   └── 3_benchmark.py               # Part 3: 성능 벤치마크
└── notebooks/
    └── model_optimization.ipynb      # Jupyter Notebook 실습
```

---

## 🔧 사전 요구사항

### 필수 조건
- ✅ Lab 2-1 완료 (FastAPI 서빙)
- ✅ Lab 2-2 완료 (MLflow Tracking)
- ✅ Python 3.9+ 환경

### 필수 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 📚 Part 1: ONNX 변환 (15분)

### 학습 목표
- ONNX 포맷의 장점 이해
- Scikit-learn 모델을 ONNX로 변환
- ONNX Runtime으로 추론 실행

### Step 1-1: 환경 변수 설정

```bash
export USER_NUM="01"  # ⚠️ 본인 번호로 변경!
export NAMESPACE="kubeflow-user${USER_NUM}"
```

### Step 1-2: ONNX 변환 실행

```bash
cd lab2-4_model-optimization
python scripts/1_onnx_conversion.py
```

**예상 출력:**
```
============================================================
  Lab 2-4 Part 1: ONNX Conversion
============================================================

Step 1: 모델 학습
────────────────────────────────────────
  ✅ RandomForest 모델 학습 완료
     - 학습 데이터: 120 samples
     - 테스트 정확도: 0.9667

Step 2: ONNX 변환
────────────────────────────────────────
  🔄 skl2onnx로 변환 중...
  ✅ ONNX 변환 완료!
     - 입력 형식: float32 [batch, 4]
     - 출력 형식: int64 [batch], float32 [batch, 3]

Step 3: 모델 파일 비교
────────────────────────────────────────
  📦 원본 모델 (joblib): 152.3 KB
  📦 ONNX 모델:         48.7 KB
  📉 크기 감소:         68.0%

Step 4: 추론 검증
────────────────────────────────────────
  ✅ 원본 모델 예측: [0, 1, 2]
  ✅ ONNX 모델 예측: [0, 1, 2]
  ✅ 예측 결과 일치!

============================================================
  ✅ Part 1 완료! 생성된 파일:
     - model_original.joblib
     - model_optimized.onnx
============================================================
```

### Step 1-3: 코드 이해

```python
# ONNX 변환 핵심 코드
import skl2onnx
from skl2onnx.common.data_types import FloatTensorType

# 입력 형식 정의
initial_type = [('float_input', FloatTensorType([None, 4]))]

# 변환 실행
onnx_model = skl2onnx.convert_sklearn(
    model, 
    initial_types=initial_type,
    target_opset=12
)

# 저장
with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

---

## ⚡ Part 2: 양자화 적용 (10분)

### 학습 목표
- 동적 양자화(Dynamic Quantization) 이해
- INT8 양자화 적용
- 모델 크기 및 정확도 비교

### Step 2-1: 양자화 실행

```bash
python scripts/2_quantization.py
```

**예상 출력:**
```
============================================================
  Lab 2-4 Part 2: Quantization
============================================================

Step 1: 동적 양자화 적용
────────────────────────────────────────
  🔄 ONNX Runtime Quantization 적용 중...
  ✅ 양자화 완료!

Step 2: 모델 크기 비교
────────────────────────────────────────
  📦 원본 ONNX:        48.7 KB
  📦 양자화 ONNX:      15.2 KB
  📉 추가 크기 감소:   68.8%
  📉 원본 대비 총:     90.0% 감소

Step 3: 정확도 비교
────────────────────────────────────────
  🎯 원본 모델 정확도:    96.67%
  🎯 ONNX 모델 정확도:    96.67%
  🎯 양자화 모델 정확도:  96.67%
  ✅ 정확도 손실 없음!

============================================================
  ✅ Part 2 완료! 생성된 파일:
     - model_quantized.onnx
============================================================
```

### Step 2-2: 양자화 코드 이해

```python
from onnxruntime.quantization import quantize_dynamic, QuantType

# 동적 양자화 적용
quantize_dynamic(
    model_input="model_optimized.onnx",
    model_output="model_quantized.onnx",
    weight_type=QuantType.QUInt8
)
```

---

## 📊 Part 3: 성능 벤치마크 (15분)

### 학습 목표
- 추론 시간 측정 방법
- MLflow에 성능 메트릭 기록
- 최적화 효과 분석

### Step 3-1: 벤치마크 실행

```bash
python scripts/3_benchmark.py
```

**예상 출력:**
```
============================================================
  Lab 2-4 Part 3: Performance Benchmark
============================================================

벤치마크 설정
────────────────────────────────────────
  - 반복 횟수: 1000회
  - 배치 크기: 1
  - 웜업: 100회

추론 시간 측정 중...
────────────────────────────────────────

결과 요약
============================================================
| 모델          | 평균 시간  | 표준편차  | 상대 속도 |
|---------------|-----------|----------|----------|
| Original      | 0.892 ms  | 0.045 ms | 1.00x    |
| ONNX          | 0.124 ms  | 0.012 ms | 7.19x    |
| ONNX Quant    | 0.098 ms  | 0.008 ms | 9.10x    |
============================================================

최적화 효과 요약
────────────────────────────────────────
  📦 모델 크기: 152.3 KB → 15.2 KB (90% 감소)
  ⚡ 추론 속도: 0.892 ms → 0.098 ms (9.1배 향상)
  🎯 정확도:    96.67% (손실 없음)

MLflow 기록
────────────────────────────────────────
  ✅ 메트릭 기록 완료
     - Experiment: model-optimization
     - Run ID: abc123...

============================================================
  ✅ Part 3 완료!
============================================================
```

### Step 3-2: MLflow에서 결과 확인

1. MLflow UI 접속: `http://localhost:5000`
2. **Experiments** → **model-optimization** 선택
3. 기록된 메트릭 확인:
   - `original_inference_time_ms`
   - `onnx_inference_time_ms`
   - `quantized_inference_time_ms`
   - `model_size_reduction_percent`
   - `speed_improvement_factor`

---

## 🎓 핵심 개념 정리

### ONNX (Open Neural Network Exchange)

```
┌─────────────────────────────────────────────────────────┐
│                    ONNX의 장점                          │
├─────────────────────────────────────────────────────────┤
│ 1. 프레임워크 호환성                                     │
│    PyTorch, TensorFlow, Scikit-learn → ONNX → 어디서든  │
│                                                         │
│ 2. 최적화된 런타임                                       │
│    ONNX Runtime은 다양한 하드웨어에 최적화               │
│                                                         │
│ 3. 엣지 배포 용이                                        │
│    작은 모델 크기, 빠른 추론, 다양한 플랫폼 지원          │
└─────────────────────────────────────────────────────────┘
```

### 양자화 종류

| 종류 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **동적 양자화** | 추론 시 가중치만 양자화 | 간단, 학습 불필요 | 제한적 속도 향상 |
| **정적 양자화** | 가중치 + 활성화 양자화 | 최고 속도 | 캘리브레이션 필요 |
| **양자화 인식 학습** | 학습 중 양자화 시뮬레이션 | 정확도 유지 | 재학습 필요 |

### 자동차 업계 적용 사례

```
┌─────────────────────────────────────────────────────────┐
│              자동차 엣지 디바이스 배포                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Cloud]                    [Edge Device]               │
│  ┌─────────┐               ┌─────────────┐              │
│  │ 원본    │    ONNX      │ 차량 ECU    │              │
│  │ PyTorch │ ──변환──→    │ (INT8 양자화)│              │
│  │ 모델    │              │ 실시간 추론  │              │
│  └─────────┘               └─────────────┘              │
│                                                         │
│  예시:                                                  │
│  - 운전자 졸음 감지                                      │
│  - 차선 이탈 경고                                        │
│  - 객체 인식 (보행자, 차량)                              │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ 실습 완료 체크리스트

### Part 1: ONNX 변환
- [ ] `1_onnx_conversion.py` 실행 완료
- [ ] `model_optimized.onnx` 파일 생성 확인
- [ ] 모델 크기 감소 확인 (약 68%)
- [ ] 예측 결과 일치 확인

### Part 2: 양자화
- [ ] `2_quantization.py` 실행 완료
- [ ] `model_quantized.onnx` 파일 생성 확인
- [ ] 추가 크기 감소 확인 (총 약 90%)
- [ ] 정확도 손실 없음 확인

### Part 3: 벤치마크
- [ ] `3_benchmark.py` 실행 완료
- [ ] 추론 속도 향상 확인 (약 7-9배)
- [ ] MLflow에 메트릭 기록 확인

---

## 🔗 다음 단계 (선택)

1. **KServe에 ONNX 모델 배포**
   - ONNX Runtime Triton Server 사용
   - 프로덕션 환경 최적화

2. **TensorRT 적용** (NVIDIA GPU)
   - 추가 속도 향상 가능
   - GPU 특화 최적화

3. **OpenVINO 적용** (Intel CPU)
   - Intel 하드웨어 최적화
   - 엣지 디바이스 배포

---

## 📚 참고 자료

- [ONNX 공식 문서](https://onnx.ai/)
- [ONNX Runtime](https://onnxruntime.ai/)
- [skl2onnx 문서](https://onnx.ai/sklearn-onnx/)
- [ONNX Quantization](https://onnxruntime.ai/docs/performance/quantization.html)

---

*© 2025 현대오토에버 MLOps Training - Lab 2-4 (Bonus)*
