"""
Lab 3-2: 모델 평가 컴포넌트
==========================

모델 성능을 평가하고 배포 결정을 내리는 컴포넌트
"""

from kfp.components import create_component_from_func


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
    print("  Component: Evaluate Model")
    print("=" * 50)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    # Run 정보 가져오기
    print(f"\n  Run ID: {run_id}")
    
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    
    # 메트릭 가져오기
    r2 = float(run.data.metrics.get("r2", 0))
    rmse = float(run.data.metrics.get("rmse", 0))
    mae = float(run.data.metrics.get("mae", 0))
    
    print(f"\n  📊 모델 성능:")
    print(f"     - R2 Score: {r2:.4f}")
    print(f"     - RMSE: {rmse:.4f}")
    print(f"     - MAE: {mae:.4f}")
    
    print(f"\n  🎯 배포 기준:")
    print(f"     - R2 Threshold: {r2_threshold}")
    
    # 배포 결정
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"\n  ✅ 결정: DEPLOY")
        print(f"     R2 ({r2:.4f}) >= Threshold ({r2_threshold})")
    else:
        decision = "skip"
        print(f"\n  ⚠️ 결정: SKIP")
        print(f"     R2 ({r2:.4f}) < Threshold ({r2_threshold})")
        print(f"     모델 성능이 기준에 미달합니다.")
    
    # 결정을 MLflow에 기록
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("deployment_decision", decision)
        mlflow.log_metric("r2_threshold", r2_threshold)
    
    return decision


# 컴포넌트 직접 실행 시
if __name__ == "__main__":
    # 테스트
    result = evaluate_model.python_func(
        run_id="test-run-id",
        mlflow_tracking_uri="http://localhost:5000",
        r2_threshold=0.8
    )
    print(f"\n결과: {result}")
