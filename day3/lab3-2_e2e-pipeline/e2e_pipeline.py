"""
Lab 3-2: End-to-End ML Pipeline
================================

데이터 로드 → 전처리 → 학습 → 평가 → 배포까지
완전 자동화된 MLOps 파이프라인

실행:
    python e2e_pipeline.py
"""

import kfp
from kfp import dsl
from kfp.components import create_component_from_func
from kfp import compiler


# ============================================================
# Component 1: 데이터 로드
# ============================================================

@create_component_from_func
def load_data(
    data_source: str = "sklearn"
) -> str:
    """
    데이터를 로드하고 저장합니다.
    
    Args:
        data_source: 데이터 소스 ("sklearn" 또는 S3 경로)
    
    Returns:
        저장된 데이터 파일 경로
    """
    import pandas as pd
    from sklearn.datasets import fetch_california_housing
    
    print("=" * 50)
    print("  Step 1: Load Data")
    print("=" * 50)
    
    # 데이터 로드
    if data_source == "sklearn":
        data = fetch_california_housing()
        df = pd.DataFrame(data.data, columns=data.feature_names)
        df['target'] = data.target
    else:
        # S3에서 로드하는 경우
        df = pd.read_csv(data_source)
    
    # 저장
    output_path = "/tmp/raw_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"  ✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"  ✅ Saved to: {output_path}")
    
    return output_path


# ============================================================
# Component 2: 전처리
# ============================================================

@create_component_from_func
def preprocess(
    data_path: str,
    test_size: float = 0.2
) -> str:
    """
    데이터 전처리 및 Train/Test 분할
    
    Args:
        data_path: 입력 데이터 경로
        test_size: 테스트 세트 비율
    
    Returns:
        전처리된 데이터 경로
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import json
    
    print("=" * 50)
    print("  Step 2: Preprocess")
    print("=" * 50)
    
    # 데이터 로드
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df)} rows")
    
    # 피처와 타겟 분리
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    # 정규화
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 저장
    output_dir = "/tmp/processed"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(f"{output_dir}/X_train.npy", X_train_scaled)
    np.save(f"{output_dir}/X_test.npy", X_test_scaled)
    np.save(f"{output_dir}/y_train.npy", y_train.values)
    np.save(f"{output_dir}/y_test.npy", y_test.values)
    
    # 메타데이터 저장
    metadata = {
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_features": X_train.shape[1],
        "feature_names": list(X.columns)
    }
    with open(f"{output_dir}/metadata.json", "w") as f:
        json.dump(metadata, f)
    
    print(f"  ✅ Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"  ✅ Saved to: {output_dir}")
    
    return output_dir


# ============================================================
# Component 3: 피처 엔지니어링
# ============================================================

@create_component_from_func
def feature_engineering(
    data_dir: str
) -> str:
    """
    피처 엔지니어링 수행
    
    Args:
        data_dir: 전처리된 데이터 디렉토리
    
    Returns:
        피처 엔지니어링 완료된 데이터 디렉토리
    """
    import numpy as np
    import json
    
    print("=" * 50)
    print("  Step 3: Feature Engineering")
    print("=" * 50)
    
    # 데이터 로드
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    
    with open(f"{data_dir}/metadata.json", "r") as f:
        metadata = json.load(f)
    
    feature_names = metadata["feature_names"]
    
    # 피처 인덱스 찾기
    # California Housing: MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Lat, Long
    rooms_idx = feature_names.index("AveRooms") if "AveRooms" in feature_names else 2
    bedrms_idx = feature_names.index("AveBedrms") if "AveBedrms" in feature_names else 3
    
    # 새 피처: 방당 침실 비율
    bedroom_ratio_train = X_train[:, bedrms_idx] / (X_train[:, rooms_idx] + 1e-6)
    bedroom_ratio_test = X_test[:, bedrms_idx] / (X_test[:, rooms_idx] + 1e-6)
    
    # 피처 추가
    X_train_new = np.column_stack([X_train, bedroom_ratio_train])
    X_test_new = np.column_stack([X_test, bedroom_ratio_test])
    
    # 저장
    output_dir = "/tmp/featured"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(f"{output_dir}/X_train.npy", X_train_new)
    np.save(f"{output_dir}/X_test.npy", X_test_new)
    
    # y 데이터 복사
    import shutil
    shutil.copy(f"{data_dir}/y_train.npy", f"{output_dir}/y_train.npy")
    shutil.copy(f"{data_dir}/y_test.npy", f"{output_dir}/y_test.npy")
    
    # 메타데이터 업데이트
    metadata["feature_names"].append("bedroom_ratio")
    metadata["n_features"] += 1
    with open(f"{output_dir}/metadata.json", "w") as f:
        json.dump(metadata, f)
    
    print(f"  ✅ Added feature: bedroom_ratio")
    print(f"  ✅ New shape: {X_train_new.shape}")
    print(f"  ✅ Saved to: {output_dir}")
    
    return output_dir


# ============================================================
# Component 4: 모델 학습 + MLflow
# ============================================================

@create_component_from_func
def train_model(
    data_dir: str,
    mlflow_tracking_uri: str,
    experiment_name: str = "e2e-pipeline",
    n_estimators: int = 100,
    max_depth: int = 10
) -> str:
    """
    모델 학습 및 MLflow에 기록
    
    Args:
        data_dir: 학습 데이터 디렉토리
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: 실험 이름
        n_estimators: 트리 개수
        max_depth: 최대 깊이
    
    Returns:
        MLflow Run ID
    """
    import numpy as np
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    import os
    
    print("=" * 50)
    print("  Step 4: Train Model")
    print("=" * 50)
    
    # 환경 변수 설정
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    
    # 데이터 로드
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")
    
    print(f"  Train: {X_train.shape}, Test: {X_test.shape}")
    
    # MLflow 설정
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    # 학습 및 기록
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        
        # 파라미터 기록
        mlflow.log_params({
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42
        })
        
        # 모델 학습
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # 평가
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # 메트릭 기록
        mlflow.log_metrics({
            "mse": mse,
            "rmse": np.sqrt(mse),
            "r2": r2
        })
        
        # 모델 저장
        mlflow.sklearn.log_model(
            model, "model",
            registered_model_name="e2e-california-model"
        )
        
        print(f"  ✅ Model trained!")
        print(f"  ✅ R2: {r2:.4f}, RMSE: {np.sqrt(mse):.4f}")
        print(f"  ✅ Run ID: {run_id}")
    
    return run_id


# ============================================================
# Component 5: 모델 평가 (조건 분기용)
# ============================================================

@create_component_from_func
def evaluate_model(
    run_id: str,
    mlflow_tracking_uri: str,
    r2_threshold: float = 0.8
) -> str:
    """
    모델 성능 평가 및 배포 결정
    
    Args:
        run_id: MLflow Run ID
        mlflow_tracking_uri: MLflow 서버 URI
        r2_threshold: R2 임계값
    
    Returns:
        "deploy" 또는 "skip"
    """
    import mlflow
    import os
    
    print("=" * 50)
    print("  Step 5: Evaluate Model")
    print("=" * 50)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    # Run 정보 가져오기
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    
    r2 = float(run.data.metrics.get("r2", 0))
    
    print(f"  Run ID: {run_id}")
    print(f"  R2 Score: {r2:.4f}")
    print(f"  Threshold: {r2_threshold}")
    
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"  ✅ Decision: DEPLOY (R2 >= threshold)")
    else:
        decision = "skip"
        print(f"  ⚠️  Decision: SKIP (R2 < threshold)")
    
    return decision


# ============================================================
# Component 6: KServe 배포
# ============================================================

@create_component_from_func
def deploy_model(
    run_id: str,
    model_name: str,
    namespace: str,
    mlflow_tracking_uri: str
):
    """
    KServe InferenceService로 모델 배포
    
    Args:
        run_id: MLflow Run ID
        model_name: 모델 이름
        namespace: Kubernetes 네임스페이스
        mlflow_tracking_uri: MLflow 서버 URI
    """
    from kubernetes import client, config
    import os
    
    print("=" * 50)
    print("  Step 6: Deploy Model")
    print("=" * 50)
    
    # Kubernetes 설정
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    
    # InferenceService 정의
    isvc = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": model_name,
            "namespace": namespace,
            "annotations": {
                "mlflow.run_id": run_id
            }
        },
        "spec": {
            "predictor": {
                "sklearn": {
                    "storageUri": f"s3://mlflow-artifacts/{run_id}/artifacts/model",
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
    
    # 배포
    api = client.CustomObjectsApi()
    
    try:
        # 기존 리소스 삭제 (있으면)
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        print(f"  ⚠️  Deleted existing InferenceService: {model_name}")
    except:
        pass
    
    # 새로 생성
    api.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=isvc
    )
    
    print(f"  ✅ InferenceService created: {model_name}")
    print(f"  ✅ Namespace: {namespace}")
    print(f"  ✅ Run ID: {run_id}")


# ============================================================
# Component 7: 알림 (배포 스킵 시)
# ============================================================

@create_component_from_func
def send_alert(
    run_id: str,
    message: str = "Model did not meet performance threshold"
):
    """
    성능 미달 시 알림 발송
    
    Args:
        run_id: MLflow Run ID
        message: 알림 메시지
    """
    print("=" * 50)
    print("  Step 6 (Alt): Send Alert")
    print("=" * 50)
    
    print(f"  ⚠️  ALERT: {message}")
    print(f"  Run ID: {run_id}")
    print(f"  Action: Please review the model and retrain if needed")
    
    # 실제 환경에서는 Slack, Email 등으로 알림 발송
    # import requests
    # requests.post(webhook_url, json={"text": message})


# ============================================================
# Pipeline Definition
# ============================================================

@dsl.pipeline(
    name='E2E ML Pipeline',
    description='End-to-End Machine Learning Pipeline with MLflow and KServe'
)
def e2e_ml_pipeline(
    data_source: str = "sklearn",
    mlflow_tracking_uri: str = "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000",
    experiment_name: str = "e2e-pipeline",
    model_name: str = "california-model",
    namespace: str = "kubeflow-user01",
    n_estimators: int = 100,
    max_depth: int = 10,
    r2_threshold: float = 0.8
):
    """
    E2E ML Pipeline
    
    데이터 로드 → 전처리 → 피처 엔지니어링 → 학습 → 평가 → 배포
    
    Args:
        data_source: 데이터 소스
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: MLflow 실험 이름
        model_name: 배포할 모델 이름
        namespace: Kubernetes 네임스페이스
        n_estimators: RandomForest 트리 개수
        max_depth: RandomForest 최대 깊이
        r2_threshold: 배포 결정 R2 임계값
    """
    
    # Step 1: 데이터 로드
    load_task = load_data(data_source=data_source)
    
    # Step 2: 전처리
    preprocess_task = preprocess(data_path=load_task.output)
    
    # Step 3: 피처 엔지니어링
    feature_task = feature_engineering(data_dir=preprocess_task.output)
    
    # Step 4: 모델 학습
    train_task = train_model(
        data_dir=feature_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name,
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    
    # Step 5: 평가
    evaluate_task = evaluate_model(
        run_id=train_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        r2_threshold=r2_threshold
    )
    
    # Step 6: 조건 분기 - 배포 또는 알림
    with dsl.Condition(evaluate_task.output == "deploy"):
        deploy_model(
            run_id=train_task.output,
            model_name=model_name,
            namespace=namespace,
            mlflow_tracking_uri=mlflow_tracking_uri
        )
    
    with dsl.Condition(evaluate_task.output == "skip"):
        send_alert(
            run_id=train_task.output,
            message="Model R2 score below threshold"
        )


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    # 파이프라인 컴파일
    print("=" * 60)
    print("  Compiling E2E Pipeline...")
    print("=" * 60)
    
    pipeline_file = 'e2e_pipeline.yaml'
    compiler.Compiler().compile(
        pipeline_func=e2e_ml_pipeline,
        package_path=pipeline_file
    )
    print(f"✅ Pipeline compiled: {pipeline_file}")
    
    # 파이프라인 실행
    try:
        print("\n" + "=" * 60)
        print("  Submitting Pipeline...")
        print("=" * 60)
        
        client = kfp.Client()
        
        run = client.create_run_from_pipeline_func(
            e2e_ml_pipeline,
            arguments={
                'data_source': 'sklearn',
                'experiment_name': 'e2e-pipeline',
                'model_name': 'california-model',
                'namespace': 'kubeflow-user01',  # 자신의 네임스페이스로 변경!
                'n_estimators': 100,
                'max_depth': 10,
                'r2_threshold': 0.75
            },
            experiment_name='e2e-experiment',
            run_name='e2e-run-001'
        )
        
        print(f"✅ Pipeline submitted!")
        print(f"   Run ID: {run.run_id}")
        print("\n💡 Check the Kubeflow Dashboard → Runs")
        
    except Exception as e:
        print(f"⚠️  Could not submit pipeline: {e}")
        print(f"\n✅ Pipeline YAML file created: {pipeline_file}")
        print("   Upload via Kubeflow UI → Pipelines → Upload Pipeline")
