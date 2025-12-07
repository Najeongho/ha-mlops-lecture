# 🎯 조별 프로젝트: E2E ML Pipeline 구축

## 📋 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **시간** | 50분 (구현) + 90분 (발표) |
| **인원** | 5명 × 6조 |
| **목표** | California Housing 가격 예측 E2E 파이프라인 |

## 🎯 요구사항

### 필수 요구사항 (70점)

| 항목 | 배점 | 설명 |
|------|------|------|
| Kubeflow Pipeline | 40점 | 최소 4개 컴포넌트, Succeeded 상태 |
| MLflow Tracking | 20점 | 최소 2회 Run, 파라미터/메트릭 기록 |
| Feature Engineering | 10점 | 1개 이상 파생 피처 생성 |

### 선택 요구사항 (30점 + 보너스)

| 항목 | 배점 | 설명 |
|------|------|------|
| KServe 배포 | 25점 | InferenceService 생성 및 API 테스트 |
| Canary 배포 | 5점 (보너스) | 트래픽 분할 적용 |

## 📁 프로젝트 구조

```
project/
├── template/
│   ├── project_pipeline.py      # 시작 템플릿
│   ├── project_pipeline.ipynb   # Notebook 버전
│   └── requirements.txt         # 의존성
└── examples/
    └── solution_pipeline.py     # 예제 솔루션 (발표 후 공개)
```

## 🚀 빠른 시작

```bash
# 템플릿으로 시작
cd project/template
cp project_pipeline.py my_team_pipeline.py

# 코드 작성 후 실행
python my_team_pipeline.py
```

## 👥 역할 분담 권장

| 역할 | 담당 업무 | 담당자 |
|------|----------|--------|
| 데이터 담당 | load_data, preprocess 컴포넌트 | - |
| 피처 담당 | feature_engineering 컴포넌트 | - |
| 학습 담당 | train_model + MLflow 연동 | - |
| 배포 담당 | evaluate, deploy (KServe) | - |
| 발표 담당 | 발표 자료 준비, 시연 | - |

## 📊 데이터셋

California Housing Dataset:
- 20,640 샘플
- 8개 피처 + 1개 타겟

| 피처 | 설명 |
|------|------|
| MedInc | 중간 소득 |
| HouseAge | 주택 연령 |
| AveRooms | 평균 방 수 |
| AveBedrms | 평균 침실 수 |
| Population | 인구 |
| AveOccup | 평균 거주자 수 |
| Latitude | 위도 |
| Longitude | 경도 |
| **target** | 중간 주택 가격 (만 달러) |

## 💡 피처 엔지니어링 아이디어

```python
# 아이디어 1: 방당 침실 비율
df['bedroom_ratio'] = df['AveBedrms'] / df['AveRooms']

# 아이디어 2: 가구당 인구
df['people_per_household'] = df['Population'] / df['AveOccup']

# 아이디어 3: 소득 구간
df['income_category'] = pd.cut(df['MedInc'], bins=5, labels=[1,2,3,4,5])

# 아이디어 4: 위치 기반 (Bay Area 근접도)
bay_area_lat, bay_area_long = 37.77, -122.42
df['dist_to_bay'] = np.sqrt(
    (df['Latitude'] - bay_area_lat)**2 + 
    (df['Longitude'] - bay_area_long)**2
)
```

## 🎤 발표 형식 (15분/조)

1. **팀 소개** (1분) - 팀원, 역할
2. **아키텍처** (2분) - 파이프라인 구조
3. **피처 엔지니어링** (2분) - 추가 피처 설명
4. **시연** (4분) - Kubeflow, MLflow, API
5. **트러블슈팅** (1분) - 겪은 문제와 해결
6. **Q&A** (5분) - 질의응답

## ✅ 체크리스트

### 구현 체크리스트

- [ ] load_data 컴포넌트 구현
- [ ] preprocess 컴포넌트 구현
- [ ] feature_engineering 컴포넌트 구현 (파생 피처 1개+)
- [ ] train_model 컴포넌트 구현 (MLflow 연동)
- [ ] 파이프라인 컴파일 성공
- [ ] 파이프라인 실행 Succeeded
- [ ] MLflow UI에서 실험 확인
- [ ] (선택) KServe 배포 성공
- [ ] (선택) API 테스트 성공

### 발표 체크리스트

- [ ] 발표 자료 준비
- [ ] 시연 준비 (화면 공유)
- [ ] Q&A 예상 질문 준비
