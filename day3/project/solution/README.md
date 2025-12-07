# 📁 Day 3 프로젝트 솔루션

이 폴더는 **강사용** 참고 솔루션입니다. 수강생에게는 `template/` 폴더의 템플릿 코드만 제공합니다.

---

## 📄 파일 목록

| 파일명 | 설명 | 평가 항목 |
|--------|------|----------|
| `project_solution.py` | 완성된 E2E 파이프라인 코드 | 전체 (100점) |
| `inference-service.yaml` | KServe 배포 YAML | KServe 배포 (25점) |

---

## 🎯 솔루션 핵심 포인트

### 1. Pipeline 구성 (40점)
```
load_data → feature_engineering → preprocess_data → train_model → evaluate → deploy
```
- 6개 컴포넌트가 순차적으로 연결
- 조건부 배포 (`dsl.Condition`) 적용
- 모든 Input/Output 타입 명시

### 2. MLflow 연동 (20점)
```python
with mlflow.start_run(run_name=f"{team_name}-training"):
    mlflow.log_params(params)              # 하이퍼파라미터
    mlflow.log_metric("r2_score", r2)      # 메트릭
    mlflow.set_tag("team", team_name)      # 태그
    mlflow.sklearn.log_model(model, ...)   # 모델 등록
```

### 3. Feature Engineering (15점)
5개 파생 변수 생성:
1. `rooms_per_household` - 가구당 총 방 수
2. `bedrooms_per_room` - 방당 침실 비율
3. `population_per_household` - 가구당 인구
4. `income_category` - 소득 구간 (1-5)
5. `location_cluster` - 위치 클러스터 (SF/LA 근접도)

### 4. KServe 배포 (25점)
```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: ${TEAM_NAME}-housing-predictor
spec:
  predictor:
    sklearn:
      storageUri: "s3://${S3_BUCKET}/models/..."
```

---

## 🚀 실행 방법

### 컴파일
```bash
cd /path/to/solution
python project_solution.py
```

### 파이프라인 업로드 및 실행
1. Kubeflow UI → Pipelines → Upload Pipeline
2. `california_housing_pipeline.yaml` 업로드
3. Create Run → 파라미터 입력
4. Start

### KServe 배포 확인
```bash
# InferenceService 상태 확인
kubectl get inferenceservice -n ${USER_NAMESPACE}

# 엔드포인트 테스트
curl -X POST \
  http://${TEAM_NAME}-housing-predictor.${USER_NAMESPACE}.svc.cluster.local/v1/models/${TEAM_NAME}-housing-predictor:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": [[8.3252, 41.0, 6.984, 1.0238, 322.0, 2.555, 37.88, -122.23, 17.87, 0.146, 126.0, 3, 0]]}'
```

---

## 📊 예상 결과

| 메트릭 | 예상 값 |
|--------|---------|
| R² Score | 0.80 ~ 0.85 |
| RMSE | 0.45 ~ 0.55 |
| MAE | 0.30 ~ 0.40 |

---

## ⚠️ 주의사항

1. **이 폴더는 강사용입니다** - 수강생에게 직접 제공하지 마세요
2. 수강생이 막힐 경우 **힌트 수준**으로 일부만 공개하세요
3. 발표 평가 시 **코드 복사 여부**를 확인하세요

---

## 📝 채점 가이드

### Pipeline 구성 (40점)
- [ ] 모든 컴포넌트 정의 (20점)
- [ ] 컴포넌트 간 연결 정상 (10점)
- [ ] 파이프라인 실행 성공 (10점)

### MLflow 연동 (20점)
- [ ] Experiment 생성 (5점)
- [ ] Parameters 로깅 (5점)
- [ ] Metrics 로깅 (5점)
- [ ] Model 등록 (5점)

### Feature Engineering (15점)
- [ ] 파생 변수 2개 이상 (10점)
- [ ] 파생 변수 3개 이상 (추가 5점)

### KServe 배포 (25점)
- [ ] InferenceService YAML 작성 (10점)
- [ ] 배포 성공 (Ready 상태) (10점)
- [ ] API 테스트 성공 (5점)

---

**강의 문의: MLOps 교육팀**
