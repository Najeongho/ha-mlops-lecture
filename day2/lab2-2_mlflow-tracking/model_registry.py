"""
Lab 2-2: MLflow Model Registry
==============================

MLflow Model Registry를 사용하여 모델 버전 및 스테이지를 관리합니다.

실행:
    python model_registry.py
"""

import mlflow
from mlflow.tracking import MlflowClient
from mlflow_config import configure_mlflow


def list_registered_models(client: MlflowClient):
    """등록된 모델 목록을 출력합니다."""
    print("\n[1] Registered Models")
    print("-" * 50)
    
    models = client.search_registered_models()
    
    if not models:
        print("  No registered models found.")
        return None
    
    for model in models:
        print(f"\n  📦 {model.name}")
        print(f"     Description: {model.description or 'N/A'}")
        print(f"     Latest versions:")
        
        for version in model.latest_versions:
            print(f"       - v{version.version}: {version.current_stage}")
    
    return models


def list_model_versions(client: MlflowClient, model_name: str):
    """특정 모델의 모든 버전을 출력합니다."""
    print(f"\n[2] Versions of '{model_name}'")
    print("-" * 50)
    
    versions = client.search_model_versions(f"name='{model_name}'")
    
    for v in versions:
        print(f"\n  Version {v.version}")
        print(f"    Stage: {v.current_stage}")
        print(f"    Status: {v.status}")
        print(f"    Run ID: {v.run_id[:8]}...")
        print(f"    Created: {v.creation_timestamp}")
    
    return versions


def transition_to_staging(client: MlflowClient, model_name: str, version: int):
    """모델 버전을 Staging으로 전환합니다."""
    print(f"\n[3] Transitioning v{version} to Staging")
    print("-" * 50)
    
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Staging"
    )
    
    print(f"  ✅ Model '{model_name}' v{version} → Staging")


def transition_to_production(client: MlflowClient, model_name: str, version: int):
    """모델 버전을 Production으로 전환합니다."""
    print(f"\n[4] Transitioning v{version} to Production")
    print("-" * 50)
    
    # 기존 Production 버전 Archived로 이동
    versions = client.search_model_versions(f"name='{model_name}'")
    for v in versions:
        if v.current_stage == "Production":
            client.transition_model_version_stage(
                name=model_name,
                version=v.version,
                stage="Archived"
            )
            print(f"  📦 v{v.version}: Production → Archived")
    
    # 새 버전 Production으로 전환
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production"
    )
    
    print(f"  ✅ Model '{model_name}' v{version} → Production")


def load_production_model(model_name: str):
    """Production 스테이지의 모델을 로드합니다."""
    print(f"\n[5] Loading Production Model")
    print("-" * 50)
    
    model_uri = f"models:/{model_name}/Production"
    print(f"  URI: {model_uri}")
    
    try:
        model = mlflow.sklearn.load_model(model_uri)
        print(f"  ✅ Model loaded successfully!")
        print(f"  Type: {type(model).__name__}")
        
        # 테스트 예측
        test_input = [[8.3252, 41.0, 6.984, 1.024, 322.0, 2.556, 37.88, -122.23]]
        prediction = model.predict(test_input)[0]
        print(f"\n  [Test Prediction]")
        print(f"  Input: {test_input[0]}")
        print(f"  Output: {prediction:.4f}")
        
        return model
        
    except Exception as e:
        print(f"  ❌ Failed to load model: {e}")
        return None


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("  Lab 2-2: MLflow Model Registry")
    print("=" * 60)
    
    # MLflow 설정
    configure_mlflow()
    
    # MLflow Client 생성
    client = MlflowClient()
    
    # 모델 이름
    model_name = "california-housing-model"
    
    # 1. 등록된 모델 목록
    models = list_registered_models(client)
    
    if not models:
        print("\n⚠️  No models registered yet.")
        print("   Run mlflow_experiment.py first to register a model.")
        return
    
    # 2. 모델 버전 목록
    versions = list_model_versions(client, model_name)
    
    if not versions:
        print(f"\n⚠️  No versions found for '{model_name}'")
        return
    
    # 최신 버전 가져오기
    latest_version = max(int(v.version) for v in versions)
    print(f"\n  Latest version: {latest_version}")
    
    # 3. Staging으로 전환
    transition_to_staging(client, model_name, latest_version)
    
    # 4. Production으로 전환
    user_input = input("\n  Promote to Production? (y/n): ")
    if user_input.lower() == 'y':
        transition_to_production(client, model_name, latest_version)
    
    # 5. Production 모델 로드
    model = load_production_model(model_name)
    
    # 최종 상태 확인
    print("\n" + "=" * 60)
    print("  Final Model Registry State")
    print("=" * 60)
    list_model_versions(client, model_name)
    
    print("\n" + "=" * 60)
    print("  ✅ Model Registry operations completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
