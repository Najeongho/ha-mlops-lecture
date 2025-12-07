"""
Day 3 프로젝트: MLOps 파이프라인 - 솔루션
==========================================

현대오토에버 MLOps 교육
KFP v1 API (kfp==1.8.22)

이 파일은 프로젝트 템플릿의 완성된 솔루션입니다.
수강생들이 직접 구현한 후 참고용으로 사용하세요.
"""

from kfp import dsl
from kfp.components import create_component_from_func
from kfp import compiler


# ============================================================
# Component 1: 데이터 로드
# ============================================================

@create_component_from_func
def load_data(dataset_name: str = "california") -> str:
    """
    데이터를 로드하고 저장합니다.
    
    Args:
        dataset_name: 데이터셋 이름
    
    Returns:
        저장된 파일 경로
    """
    import pandas as pd
    from sklearn.datasets import fetch_california_housing
    
    print("=" * 50)
    print("  Step 1: Load Data")
    print("=" * 50)
    
    if dataset_name == "california":
        data = fetch_california_housing()
        df = pd.DataFrame(data.data, columns=data.feature_names)
        df['target'] = data.target
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    
    output_path = "/tmp/raw_data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"  ✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"  ✅ Features: {list(df.columns[:-1])}")
    print(f"  ✅ Saved to: {output_path}")
    
    return output_path


# ============================================================
# Component 2: 전처리
# ============================================================

@create_component_from_func
def preprocess(data_path: str, test_size: float = 0.2) -> str:
    """
    데이터 전처리 및 Train/Test 분할
    
    Args:
        data_path: 입력 데이터 경로
        test_size: 테스트 세트 비율
    
    Returns:
        전처리된 데이터 디렉토리 경로
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import json
    import os
    
    print("=" * 50)
    print("  Step 2: Preprocess")
    print("=" * 50)
    
    # 데이터 로드
    df = pd.read_csv(data_path)
    print(f"  Loaded: {len(df)} rows")
    
    # 피처/타겟 분리
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"  ✅ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # 정규화
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 저장
    output_dir = "/tmp/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(f"{output_dir}/X_train.npy", X_train_scaled)
    np.save(f"{output_dir}/X_test.npy", X_test_scaled)
    np.save(f"{output_dir}/y_train.npy", y_train.values)
    np.save(f"{output_dir}/y_test.npy", y_test.values)
    
    # 스케일러 정보 저장
    metadata = {
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_features": X_train.shape[1],
        "feature_names": list(X.columns),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist()
    }
    
    with open(f"{output_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"  ✅ Saved to: {output_dir}")
    
    return output_dir


# ============================================================
# Component 3: 하이퍼파라미터 탐색
# ============================================================

@create_component_from_func
def hyperparameter_search(
    data_dir: str,
    mlflow_tracking_uri: str,
    experiment_name: str
) -> str:
    """
    하이퍼파라미터 탐색 수행
    
    Args:
        data_dir: 데이터 디렉토리
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: 실험 이름
    
    Returns:
        최적 하이퍼파라미터 (JSON)
    """
    import numpy as np
    import mlflow
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score
    import json
    import os
    
    print("=" * 50)
    print("  Step 3: Hyperparameter Search")
    print("=" * 50)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name + "-hp-search")
    
    # 데이터 로드
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")
    
    # 하이퍼파라미터 그리드
    param_grid = [
        {"n_estimators": 50, "max_depth": 5},
        {"n_estimators": 100, "max_depth": 10},
        {"n_estimators": 150, "max_depth": 15},
        {"n_estimators": 200, "max_depth": 10},
    ]
    
    best_score = 0
    best_params = None
    
    print(f"\n  Testing {len(param_grid)} configurations...")
    
    for params in param_grid:
        with mlflow.start_run(nested=True):
            mlflow.log_params(params)
            
            model = RandomForestRegressor(
                n_estimators=params["n_estimators"],
                max_depth=params["max_depth"],
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            
            mlflow.log_metric("r2", r2)
            
            print(f"    n_estimators={params['n_estimators']}, "
                  f"max_depth={params['max_depth']}: R2={r2:.4f}")
            
            if r2 > best_score:
                best_score = r2
                best_params = params.copy()
    
    print(f"\n  🏆 Best: n_estimators={best_params['n_estimators']}, "
          f"max_depth={best_params['max_depth']}, R2={best_score:.4f}")
    
    return json.dumps(best_params)


# ============================================================
# Component 4: 모델 학습
# ============================================================

@create_component_from_func
def train_model(
    data_dir: str,
    best_params: str,
    mlflow_tracking_uri: str,
    experiment_name: str
) -> str:
    """
    최적 하이퍼파라미터로 모델 학습
    
    Args:
        data_dir: 데이터 디렉토리
        best_params: 최적 하이퍼파라미터 (JSON)
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: 실험 이름
    
    Returns:
        MLflow Run ID
    """
    import numpy as np
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    import json
    import os
    
    print("=" * 50)
    print("  Step 4: Train Model")
    print("=" * 50)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    # 파라미터 파싱
    params = json.loads(best_params)
    print(f"  Using params: {params}")
    
    # 데이터 로드
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")
    
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        
        # 파라미터 로깅
        mlflow.log_params({
            "n_estimators": params["n_estimators"],
            "max_depth": params["max_depth"],
            "random_state": 42,
            "n_jobs": -1
        })
        
        # 모델 학습
        print("\n  Training model...")
        model = RandomForestRegressor(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # 평가
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # 메트릭 로깅
        mlflow.log_metrics({
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        })
        
        # 모델 저장
        mlflow.sklearn.log_model(
            model, "model",
            registered_model_name="project-california-model"
        )
        
        # 태그
        mlflow.set_tag("pipeline", "project")
        mlflow.set_tag("stage", "production")
        
        print(f"\n  ✅ Model trained!")
        print(f"     R2: {r2:.4f}")
        print(f"     RMSE: {rmse:.4f}")
        print(f"     Run ID: {run_id}")
    
    return run_id


# ============================================================
# Component 5: 모델 평가
# ============================================================

@create_component_from_func
def evaluate_model(
    run_id: str,
    mlflow_tracking_uri: str,
    r2_threshold: float = 0.8
) -> str:
    """
    모델 평가 및 배포 결정
    
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
    rmse = float(run.data.metrics.get("rmse", 0))
    
    print(f"  Run ID: {run_id}")
    print(f"  R2 Score: {r2:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  Threshold: {r2_threshold}")
    
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"\n  ✅ Decision: DEPLOY")
        print(f"     R2 ({r2:.4f}) >= Threshold ({r2_threshold})")
    else:
        decision = "skip"
        print(f"\n  ⚠️ Decision: SKIP")
        print(f"     R2 ({r2:.4f}) < Threshold ({r2_threshold})")
    
    # 결정 기록
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("deployment_decision", decision)
    
    return decision


# ============================================================
# Component 6: 모델 배포
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
    from kubernetes.client.rest import ApiException
    import time
    
    print("=" * 50)
    print("  Step 6: Deploy Model")
    print("=" * 50)
    
    print(f"  Model: {model_name}")
    print(f"  Namespace: {namespace}")
    print(f"  Run ID: {run_id}")
    
    # Kubernetes 설정
    try:
        config.load_incluster_config()
        print("  ✅ In-cluster config loaded")
    except:
        config.load_kube_config()
        print("  ✅ Kubeconfig loaded")
    
    model_uri = f"s3://mlflow-artifacts/{run_id}/artifacts/model"
    
    isvc = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": model_name,
            "namespace": namespace,
            "labels": {
                "app": model_name,
                "mlflow-run-id": run_id
            },
            "annotations": {
                "autoscaling.knative.dev/minScale": "1"
            }
        },
        "spec": {
            "predictor": {
                "sklearn": {
                    "storageUri": model_uri,
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "256Mi"},
                        "limits": {"cpu": "500m", "memory": "512Mi"}
                    }
                }
            }
        }
    }
    
    api = client.CustomObjectsApi()
    
    # 기존 리소스 삭제
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        print(f"  ⚠️ Deleted existing InferenceService")
        time.sleep(5)
    except ApiException as e:
        if e.status != 404:
            raise
    
    # 생성
    api.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=isvc
    )
    
    print(f"\n  ✅ InferenceService created: {model_name}")
    print(f"  Endpoint: http://{model_name}.{namespace}.svc.cluster.local")


# ============================================================
# Component 7: 알림
# ============================================================

@create_component_from_func
def send_alert(run_id: str, message: str = "Model did not meet threshold"):
    """성능 미달 알림"""
    print("=" * 50)
    print("  Step 6 (Alt): Send Alert")
    print("=" * 50)
    
    print(f"  ⚠️ ALERT: {message}")
    print(f"  Run ID: {run_id}")
    print(f"\n  Action Required:")
    print(f"    1. Check MLflow for detailed metrics")
    print(f"    2. Review training data quality")
    print(f"    3. Consider hyperparameter tuning")


# ============================================================
# Pipeline Definition
# ============================================================

@dsl.pipeline(
    name='project-mlops-pipeline',
    description='Complete MLOps Pipeline with HP Search and Conditional Deployment'
)
def project_pipeline(
    dataset_name: str = "california",
    mlflow_tracking_uri: str = "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000",
    experiment_name: str = "project-experiment",
    model_name: str = "project-model",
    namespace: str = "kubeflow-user01",
    r2_threshold: float = 0.8
):
    """
    완전한 MLOps 파이프라인
    
    Flow:
    load_data → preprocess → hp_search → train → evaluate → deploy/alert
    """
    
    # Step 1: 데이터 로드
    load_task = load_data(dataset_name=dataset_name)
    
    # Step 2: 전처리
    preprocess_task = preprocess(data_path=load_task.output)
    
    # Step 3: 하이퍼파라미터 탐색
    hp_task = hyperparameter_search(
        data_dir=preprocess_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name
    )
    
    # Step 4: 모델 학습
    train_task = train_model(
        data_dir=preprocess_task.output,
        best_params=hp_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name
    )
    
    # Step 5: 평가
    evaluate_task = evaluate_model(
        run_id=train_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        r2_threshold=r2_threshold
    )
    
    # Step 6: 조건부 배포
    with dsl.Condition(evaluate_task.output == "deploy", name="deploy-condition"):
        deploy_model(
            run_id=train_task.output,
            model_name=model_name,
            namespace=namespace,
            mlflow_tracking_uri=mlflow_tracking_uri
        )
    
    with dsl.Condition(evaluate_task.output == "skip", name="skip-condition"):
        send_alert(run_id=train_task.output)


# ============================================================
# Main - Compile Pipeline
# ============================================================

if __name__ == "__main__":
    import os
    
    print("=" * 60)
    print("  Project Pipeline - Solution")
    print("=" * 60)
    
    # 컴파일
    output_file = "project_pipeline_solution.yaml"
    
    compiler.Compiler().compile(
        pipeline_func=project_pipeline,
        package_path=output_file
    )
    
    print(f"\n✅ Pipeline compiled: {output_file}")
    print("\n📋 Next Steps:")
    print("  1. Upload to Kubeflow UI")
    print("  2. Create a Run with your parameters")
    print("  3. Monitor in Kubeflow Dashboard")
    print("  4. Check MLflow for experiments")
