"""
Lab 3-2: 모델 학습 컴포넌트
==========================

모델 학습 및 MLflow 연동을 수행하는 컴포넌트
"""

from kfp.components import create_component_from_func


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
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    import json
    import os
    
    print("=" * 50)
    print("  Component: Train Model")
    print("=" * 50)
    
    # 환경 변수 설정
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    
    # 데이터 로드
    print(f"\n  데이터 로드: {data_dir}")
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")
    
    print(f"     - X_train: {X_train.shape}")
    print(f"     - X_test: {X_test.shape}")
    
    # MLflow 설정
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    print(f"\n  📊 MLflow 설정:")
    print(f"     - Tracking URI: {mlflow_tracking_uri}")
    print(f"     - Experiment: {experiment_name}")
    
    # 학습 및 기록
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"\n  🏃 Run ID: {run_id}")
        
        # 파라미터 기록
        params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42,
            "n_jobs": -1
        }
        mlflow.log_params(params)
        print("  ✅ 파라미터 로깅 완료")
        
        # 모델 학습
        print("\n  🔄 모델 학습 중...")
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        print("  ✅ 모델 학습 완료")
        
        # 예측 및 평가
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # 메트릭 기록
        metrics = {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
        mlflow.log_metrics(metrics)
        print("  ✅ 메트릭 로깅 완료")
        
        print(f"\n  📈 모델 성능:")
        print(f"     - R2 Score: {r2:.4f}")
        print(f"     - RMSE: {rmse:.4f}")
        print(f"     - MAE: {mae:.4f}")
        
        # 모델 저장
        mlflow.sklearn.log_model(
            model, "model",
            registered_model_name="e2e-california-model"
        )
        print("  ✅ 모델 등록 완료")
        
        # 태그 추가
        mlflow.set_tag("pipeline", "e2e")
        mlflow.set_tag("stage", "training")
    
    print(f"\n  ✅ 학습 완료! Run ID: {run_id}")
    
    return run_id


# 컴포넌트 직접 실행 시
if __name__ == "__main__":
    # 테스트
    result = train_model.python_func(
        data_dir="/tmp/processed",
        mlflow_tracking_uri="http://localhost:5000",
        experiment_name="test-experiment",
        n_estimators=50,
        max_depth=5
    )
    print(f"\n결과: {result}")
