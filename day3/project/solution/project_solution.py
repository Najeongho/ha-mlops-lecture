"""
[Day 3 프로젝트] 완성 솔루션
California Housing E2E MLOps 파이프라인

평가 기준:
- Pipeline 구성 (40점): 모든 컴포넌트 연결, 실행 성공
- MLflow 연동 (20점): 실험 추적, 모델 등록
- Feature Engineering (15점): 최소 2개 이상 파생 변수
- KServe 배포 (25점): InferenceService 배포, API 테스트

현대오토에버 MLOps 교육
"""

import os
from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics
from typing import NamedTuple


# ============================================================
# 환경 변수 설정
# ============================================================
USER_NAMESPACE = os.environ.get("USER_NAMESPACE", "kubeflow-user01")
MLFLOW_TRACKING_URI = os.environ.get(
    "MLFLOW_TRACKING_URI", 
    "http://mlflow-server.mlflow-system.svc.cluster.local:5000"
)
S3_BUCKET = os.environ.get("S3_BUCKET", "mlops-training-bucket")
TEAM_NAME = os.environ.get("TEAM_NAME", "team-01")


# ============================================================
# Component 1: 데이터 로드
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.2"]
)
def load_data(output_data: Output[Dataset]):
    """California Housing 데이터셋 로드"""
    from sklearn.datasets import fetch_california_housing
    import pandas as pd
    
    print("=" * 60)
    print("Step 1: 데이터 로드")
    print("=" * 60)
    
    # 데이터 로드
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame
    
    print(f"데이터셋 크기: {df.shape}")
    print(f"피처: {list(df.columns)}")
    print(f"\n기본 통계:")
    print(df.describe())
    
    # 저장
    df.to_csv(output_data.path, index=False)
    print(f"\n✅ 데이터 저장 완료: {output_data.path}")


# ============================================================
# Component 2: 피처 엔지니어링 (15점)
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "numpy==1.24.3"]
)
def feature_engineering(
    input_data: Input[Dataset],
    output_data: Output[Dataset]
) -> dict:
    """
    피처 엔지니어링 - 파생 변수 생성
    
    생성되는 피처:
    1. rooms_per_household: 가구당 방 수
    2. bedrooms_per_room: 방당 침실 비율
    3. population_per_household: 가구당 인구
    4. income_category: 소득 구간 (범주형)
    5. location_cluster: 위치 클러스터 (해안 근접도)
    """
    import pandas as pd
    import numpy as np
    
    print("=" * 60)
    print("Step 2: 피처 엔지니어링")
    print("=" * 60)
    
    df = pd.read_csv(input_data.path)
    original_features = list(df.columns)
    
    # ===== 파생 변수 1: rooms_per_household =====
    df['rooms_per_household'] = df['AveRooms'] * df['AveOccup']
    print("✅ 파생 변수 생성: rooms_per_household (가구당 총 방 수)")
    
    # ===== 파생 변수 2: bedrooms_per_room =====
    df['bedrooms_per_room'] = df['AveBedrms'] / df['AveRooms']
    # NaN 처리
    df['bedrooms_per_room'] = df['bedrooms_per_room'].fillna(0)
    print("✅ 파생 변수 생성: bedrooms_per_room (방당 침실 비율)")
    
    # ===== 파생 변수 3: population_per_household =====
    df['population_per_household'] = df['Population'] / df['AveOccup']
    df['population_per_household'] = df['population_per_household'].replace(
        [np.inf, -np.inf], 0
    ).fillna(0)
    print("✅ 파생 변수 생성: population_per_household (가구당 인구)")
    
    # ===== 파생 변수 4: income_category =====
    df['income_category'] = pd.cut(
        df['MedInc'],
        bins=[0, 2, 4, 6, 8, np.inf],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)
    print("✅ 파생 변수 생성: income_category (소득 구간 1-5)")
    
    # ===== 파생 변수 5: location_cluster =====
    # 위도/경도 기반 해안 근접도 (단순화된 버전)
    # LA(34.05, -118.24), SF(37.77, -122.42) 기준
    la_lat, la_lon = 34.05, -118.24
    sf_lat, sf_lon = 37.77, -122.42
    
    df['dist_to_la'] = np.sqrt(
        (df['Latitude'] - la_lat)**2 + (df['Longitude'] - la_lon)**2
    )
    df['dist_to_sf'] = np.sqrt(
        (df['Latitude'] - sf_lat)**2 + (df['Longitude'] - sf_lon)**2
    )
    df['location_cluster'] = (df['dist_to_la'] < df['dist_to_sf']).astype(int)
    # 임시 컬럼 삭제
    df = df.drop(columns=['dist_to_la', 'dist_to_sf'])
    print("✅ 파생 변수 생성: location_cluster (0=SF근접, 1=LA근접)")
    
    # 결과 요약
    new_features = [col for col in df.columns if col not in original_features]
    print(f"\n📊 피처 엔지니어링 결과:")
    print(f"   - 원본 피처: {len(original_features)}개")
    print(f"   - 생성 피처: {len(new_features)}개")
    print(f"   - 최종 피처: {len(df.columns)}개")
    print(f"   - 생성된 피처 목록: {new_features}")
    
    # 저장
    df.to_csv(output_data.path, index=False)
    print(f"\n✅ 피처 엔지니어링 완료: {output_data.path}")
    
    return {
        "original_features": len(original_features),
        "new_features": len(new_features),
        "total_features": len(df.columns),
        "new_feature_names": new_features
    }


# ============================================================
# Component 3: 데이터 전처리
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.2", "joblib==1.3.2"]
)
def preprocess_data(
    input_data: Input[Dataset],
    X_train_out: Output[Dataset],
    X_test_out: Output[Dataset],
    y_train_out: Output[Dataset],
    y_test_out: Output[Dataset],
    scaler_out: Output[Model]
) -> dict:
    """데이터 분할 및 스케일링"""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import joblib
    
    print("=" * 60)
    print("Step 3: 데이터 전처리")
    print("=" * 60)
    
    df = pd.read_csv(input_data.path)
    
    # 피처와 타겟 분리
    X = df.drop(columns=['MedHouseVal'])
    y = df['MedHouseVal']
    
    print(f"피처 shape: {X.shape}")
    print(f"타겟 shape: {y.shape}")
    
    # 학습/테스트 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n학습 데이터: {X_train.shape}")
    print(f"테스트 데이터: {X_test.shape}")
    
    # 스케일링
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns
    )
    
    # 저장
    X_train_scaled.to_csv(X_train_out.path, index=False)
    X_test_scaled.to_csv(X_test_out.path, index=False)
    y_train.to_csv(y_train_out.path, index=False)
    y_test.to_csv(y_test_out.path, index=False)
    joblib.dump(scaler, scaler_out.path)
    
    print(f"\n✅ 전처리 완료")
    
    return {
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "n_features": X_train.shape[1]
    }


# ============================================================
# Component 4: 모델 학습 + MLflow 연동 (20점)
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=[
        "pandas==2.0.3", 
        "scikit-learn==1.3.2", 
        "mlflow==2.9.2",
        "boto3==1.34.0",
        "joblib==1.3.2"
    ]
)
def train_model_with_mlflow(
    X_train: Input[Dataset],
    y_train: Input[Dataset],
    X_test: Input[Dataset],
    y_test: Input[Dataset],
    mlflow_tracking_uri: str,
    experiment_name: str,
    team_name: str,
    model_out: Output[Model],
    metrics_out: Output[Metrics]
) -> NamedTuple('Outputs', [('run_id', str), ('r2_score', float), ('rmse', float)]):
    """
    모델 학습 및 MLflow 연동
    
    MLflow 연동 항목:
    - Parameters: 모든 하이퍼파라미터
    - Metrics: R2, RMSE, MAE
    - Artifacts: 모델 파일
    - Tags: 팀명, 환경 정보
    """
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    import mlflow
    import mlflow.sklearn
    import joblib
    from collections import namedtuple
    
    print("=" * 60)
    print("Step 4: 모델 학습 + MLflow 연동")
    print("=" * 60)
    
    # 데이터 로드
    X_train_df = pd.read_csv(X_train.path)
    y_train_df = pd.read_csv(y_train.path)
    X_test_df = pd.read_csv(X_test.path)
    y_test_df = pd.read_csv(y_test.path)
    
    # MLflow 설정
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    print(f"MLflow Tracking URI: {mlflow_tracking_uri}")
    print(f"Experiment: {experiment_name}")
    
    # 하이퍼파라미터 정의
    params = {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "random_state": 42,
        "n_jobs": -1
    }
    
    with mlflow.start_run(run_name=f"{team_name}-training") as run:
        run_id = run.info.run_id
        print(f"\n📝 MLflow Run ID: {run_id}")
        
        # ===== Parameters 로깅 =====
        mlflow.log_params(params)
        print("✅ Parameters 로깅 완료")
        
        # ===== Tags 설정 =====
        mlflow.set_tag("team", team_name)
        mlflow.set_tag("model_type", "RandomForestRegressor")
        mlflow.set_tag("dataset", "california_housing")
        mlflow.set_tag("feature_engineering", "enabled")
        print("✅ Tags 설정 완료")
        
        # ===== 모델 학습 =====
        print("\n🔄 모델 학습 중...")
        model = RandomForestRegressor(**params)
        model.fit(X_train_df, y_train_df.values.ravel())
        print("✅ 모델 학습 완료")
        
        # ===== 예측 및 평가 =====
        y_pred = model.predict(X_test_df)
        
        r2 = r2_score(y_test_df, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test_df, y_pred))
        mae = mean_absolute_error(y_test_df, y_pred)
        
        # ===== Metrics 로깅 =====
        mlflow.log_metric("r2_score", r2)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("n_features", X_train_df.shape[1])
        mlflow.log_metric("n_train_samples", len(X_train_df))
        print("✅ Metrics 로깅 완료")
        
        print(f"\n📊 모델 성능:")
        print(f"   - R² Score: {r2:.4f}")
        print(f"   - RMSE: {rmse:.4f}")
        print(f"   - MAE: {mae:.4f}")
        
        # ===== Feature Importance 로깅 =====
        feature_importance = pd.DataFrame({
            'feature': X_train_df.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 Top 5 Feature Importance:")
        for idx, row in feature_importance.head(5).iterrows():
            print(f"   - {row['feature']}: {row['importance']:.4f}")
        
        # Feature Importance를 artifact로 저장
        fi_path = "/tmp/feature_importance.csv"
        feature_importance.to_csv(fi_path, index=False)
        mlflow.log_artifact(fi_path)
        
        # ===== 모델 저장 및 로깅 =====
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name=f"{team_name}-housing-model"
        )
        print("✅ 모델 MLflow에 등록 완료")
        
        # 로컬 저장
        joblib.dump(model, model_out.path)
    
    # KFP Metrics 저장
    metrics_out.log_metric("r2_score", r2)
    metrics_out.log_metric("rmse", rmse)
    metrics_out.log_metric("mae", mae)
    
    print(f"\n✅ 학습 완료! Run ID: {run_id}")
    
    Outputs = namedtuple('Outputs', ['run_id', 'r2_score', 'rmse'])
    return Outputs(run_id, r2, rmse)


# ============================================================
# Component 5: 모델 평가 및 배포 결정
# ============================================================
@component(base_image="python:3.9-slim")
def evaluate_and_decide(
    r2_score: float,
    rmse: float,
    r2_threshold: float = 0.75,
    rmse_threshold: float = 0.6
) -> bool:
    """모델 성능 평가 및 배포 여부 결정"""
    
    print("=" * 60)
    print("Step 5: 배포 결정")
    print("=" * 60)
    
    print(f"현재 성능:")
    print(f"  - R² Score: {r2_score:.4f} (임계값: {r2_threshold})")
    print(f"  - RMSE: {rmse:.4f} (임계값: {rmse_threshold})")
    
    deploy = r2_score >= r2_threshold and rmse <= rmse_threshold
    
    if deploy:
        print(f"\n✅ 배포 승인! 모델이 품질 기준을 충족합니다.")
    else:
        print(f"\n❌ 배포 거부. 모델 성능이 기준 미달입니다.")
        if r2_score < r2_threshold:
            print(f"   - R² Score가 {r2_threshold} 미만입니다.")
        if rmse > rmse_threshold:
            print(f"   - RMSE가 {rmse_threshold} 초과입니다.")
    
    return deploy


# ============================================================
# Component 6: KServe 배포 (25점)
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["kubernetes==28.1.0", "boto3==1.34.0"]
)
def deploy_to_kserve(
    model: Input[Model],
    team_name: str,
    namespace: str,
    s3_bucket: str,
    run_id: str
) -> str:
    """KServe InferenceService 배포"""
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    import boto3
    import os
    import shutil
    
    print("=" * 60)
    print("Step 6: KServe 배포")
    print("=" * 60)
    
    # ===== S3 업로드 =====
    print("\n📤 모델을 S3에 업로드 중...")
    
    s3_client = boto3.client('s3')
    s3_path = f"models/{team_name}/{run_id}/model.joblib"
    
    s3_client.upload_file(model.path, s3_bucket, s3_path)
    model_uri = f"s3://{s3_bucket}/models/{team_name}/{run_id}/"
    
    print(f"✅ S3 업로드 완료: {model_uri}")
    
    # ===== InferenceService 생성 =====
    print("\n🚀 InferenceService 생성 중...")
    
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    
    api = client.CustomObjectsApi()
    
    service_name = f"{team_name}-housing-predictor"
    
    inference_service = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": service_name,
            "namespace": namespace,
            "labels": {
                "team": team_name,
                "project": "housing-prediction",
                "mlflow-run-id": run_id
            },
            "annotations": {
                "sidecar.istio.io/inject": "true"
            }
        },
        "spec": {
            "predictor": {
                "sklearn": {
                    "storageUri": model_uri,
                    "resources": {
                        "requests": {
                            "cpu": "100m",
                            "memory": "256Mi"
                        },
                        "limits": {
                            "cpu": "500m",
                            "memory": "512Mi"
                        }
                    }
                }
            }
        }
    }
    
    # 기존 서비스 삭제 (있는 경우)
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=service_name
        )
        print(f"⚠️ 기존 InferenceService '{service_name}' 삭제됨")
        import time
        time.sleep(5)  # 삭제 완료 대기
    except ApiException as e:
        if e.status != 404:
            raise
    
    # 새 서비스 생성
    result = api.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=inference_service
    )
    
    print(f"✅ InferenceService 생성 완료!")
    print(f"   - 이름: {service_name}")
    print(f"   - 네임스페이스: {namespace}")
    print(f"   - 모델 URI: {model_uri}")
    
    # 엔드포인트 URL 반환
    endpoint_url = f"http://{service_name}.{namespace}.svc.cluster.local/v1/models/{service_name}:predict"
    
    print(f"\n📡 예측 엔드포인트:")
    print(f"   {endpoint_url}")
    
    print(f"\n🧪 테스트 명령어:")
    print(f'''
curl -X POST {endpoint_url} \\
  -H "Content-Type: application/json" \\
  -d '{{"instances": [[8.3252, 41.0, 6.984, 1.0238, 322.0, 2.555, 37.88, -122.23, 17.87, 0.146, 126.0, 3, 0]]}}'
''')
    
    return endpoint_url


# ============================================================
# 전체 파이프라인 정의
# ============================================================
@dsl.pipeline(
    name="california-housing-mlops-pipeline",
    description="California Housing E2E MLOps Pipeline - 프로젝트 솔루션"
)
def housing_mlops_pipeline(
    team_name: str = "team-01",
    namespace: str = "kubeflow-user01",
    mlflow_tracking_uri: str = "http://mlflow-server.mlflow-system.svc.cluster.local:5000",
    experiment_name: str = "california-housing-project",
    s3_bucket: str = "mlops-training-bucket",
    r2_threshold: float = 0.75,
    rmse_threshold: float = 0.6
):
    """
    E2E MLOps 파이프라인
    
    파이프라인 흐름:
    
    ┌────────────┐
    │ load_data  │
    └─────┬──────┘
          │
          ▼
    ┌─────────────────────┐
    │ feature_engineering │ ← 파생 변수 5개 생성
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────┐
    │ preprocess_data │ ← 분할 + 스케일링
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ train_model_with_mlflow │ ← MLflow 연동
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────┐
    │ evaluate_and_decide │ ← 배포 결정
    └──────────┬──────────┘
               │
               ▼ (조건부)
    ┌──────────────────┐
    │ deploy_to_kserve │ ← KServe 배포
    └──────────────────┘
    """
    
    # Step 1: 데이터 로드
    load_task = load_data()
    
    # Step 2: 피처 엔지니어링
    fe_task = feature_engineering(
        input_data=load_task.outputs["output_data"]
    )
    
    # Step 3: 전처리
    preprocess_task = preprocess_data(
        input_data=fe_task.outputs["output_data"]
    )
    
    # Step 4: 모델 학습 + MLflow
    train_task = train_model_with_mlflow(
        X_train=preprocess_task.outputs["X_train_out"],
        y_train=preprocess_task.outputs["y_train_out"],
        X_test=preprocess_task.outputs["X_test_out"],
        y_test=preprocess_task.outputs["y_test_out"],
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name,
        team_name=team_name
    )
    
    # Step 5: 평가 및 배포 결정
    eval_task = evaluate_and_decide(
        r2_score=train_task.outputs["r2_score"],
        rmse=train_task.outputs["rmse"],
        r2_threshold=r2_threshold,
        rmse_threshold=rmse_threshold
    )
    
    # Step 6: KServe 배포 (조건부)
    with dsl.Condition(eval_task.output == True, name="deploy-if-approved"):
        deploy_task = deploy_to_kserve(
            model=train_task.outputs["model_out"],
            team_name=team_name,
            namespace=namespace,
            s3_bucket=s3_bucket,
            run_id=train_task.outputs["run_id"]
        )


# ============================================================
# 컴파일 및 실행
# ============================================================
if __name__ == "__main__":
    from kfp import compiler
    import os
    
    # 컴파일
    output_file = "california_housing_pipeline.yaml"
    compiler.Compiler().compile(
        pipeline_func=housing_mlops_pipeline,
        package_path=output_file
    )
    
    print("=" * 60)
    print("✅ 파이프라인 컴파일 완료!")
    print("=" * 60)
    print(f"\n📄 출력 파일: {output_file}")
    print(f"\n🚀 실행 방법:")
    print(f"   1. Kubeflow UI → Pipelines → Upload Pipeline")
    print(f"   2. '{output_file}' 업로드")
    print(f"   3. Create Run → 파라미터 입력:")
    print(f"      - team_name: 팀 이름 (예: team-01)")
    print(f"      - namespace: 네임스페이스 (예: kubeflow-user01)")
    print(f"      - s3_bucket: S3 버킷명")
    print(f"   4. Start 클릭")
    print("=" * 60)
