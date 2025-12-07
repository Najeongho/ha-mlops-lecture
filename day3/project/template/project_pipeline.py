"""
🎯 조별 프로젝트 템플릿: E2E ML Pipeline
=========================================

이 템플릿을 수정하여 팀 프로젝트를 완성하세요.

TODO 표시된 부분을 구현하세요!

실행:
    python project_pipeline.py
"""

import kfp
from kfp import dsl
from kfp.components import create_component_from_func
from kfp import compiler


# ============================================================
# TODO 1: 데이터 로드 컴포넌트
# ============================================================

@create_component_from_func
def load_data() -> str:
    """
    California Housing 데이터셋을 로드합니다.
    
    Returns:
        저장된 데이터 파일 경로
    """
    # TODO: 아래 코드를 완성하세요
    
    from sklearn.datasets import fetch_california_housing
    import pandas as pd
    
    print("=" * 50)
    print("  Step 1: Load Data")
    print("=" * 50)
    
    # 데이터 로드
    data = fetch_california_housing()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = data.target
    
    # 저장
    output_path = "/tmp/data.csv"
    df.to_csv(output_path, index=False)
    
    print(f"  ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    return output_path


# ============================================================
# TODO 2: 전처리 컴포넌트
# ============================================================

@create_component_from_func
def preprocess(data_path: str) -> str:
    """
    데이터 전처리 및 Train/Test 분할
    
    Args:
        data_path: 입력 데이터 경로
    
    Returns:
        전처리된 데이터 디렉토리 경로
    """
    # TODO: 아래 코드를 완성하세요
    
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    import os
    
    print("=" * 50)
    print("  Step 2: Preprocess")
    print("=" * 50)
    
    # 데이터 로드
    df = pd.read_csv(data_path)
    
    # 피처와 타겟 분리
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 저장
    output_dir = "/tmp/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # TODO: 데이터 저장 구현
    # 힌트: np.save()를 사용하세요
    np.save(f"{output_dir}/X_train.npy", X_train.values)
    np.save(f"{output_dir}/X_test.npy", X_test.values)
    np.save(f"{output_dir}/y_train.npy", y_train.values)
    np.save(f"{output_dir}/y_test.npy", y_test.values)
    
    print(f"  ✅ Train: {len(X_train)}, Test: {len(X_test)}")
    
    return output_dir


# ============================================================
# TODO 3: 피처 엔지니어링 컴포넌트
# ============================================================

@create_component_from_func
def feature_engineering(data_dir: str) -> str:
    """
    피처 엔지니어링 - 새로운 파생 피처 생성
    
    Args:
        data_dir: 전처리된 데이터 디렉토리
    
    Returns:
        피처 엔지니어링 완료된 데이터 디렉토리
    """
    # TODO: 새로운 피처를 1개 이상 생성하세요!
    
    import numpy as np
    import os
    
    print("=" * 50)
    print("  Step 3: Feature Engineering")
    print("=" * 50)
    
    # 데이터 로드
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    
    # =======================================
    # TODO: 파생 피처 생성 코드 작성!
    # =======================================
    # 
    # 피처 인덱스 (California Housing):
    #   0: MedInc (중간 소득)
    #   1: HouseAge (주택 연령)
    #   2: AveRooms (평균 방 수)
    #   3: AveBedrms (평균 침실 수)
    #   4: Population (인구)
    #   5: AveOccup (평균 거주자)
    #   6: Latitude (위도)
    #   7: Longitude (경도)
    #
    # 예시: 방당 침실 비율
    bedroom_ratio_train = X_train[:, 3] / (X_train[:, 2] + 1e-6)
    bedroom_ratio_test = X_test[:, 3] / (X_test[:, 2] + 1e-6)
    
    # TODO: 추가 피처를 생성하세요!
    # 예: people_per_household = Population / AveOccup
    # 예: dist_to_sf = sqrt((Lat - 37.77)^2 + (Long + 122.42)^2)
    
    # 피처 추가
    X_train_new = np.column_stack([X_train, bedroom_ratio_train])
    X_test_new = np.column_stack([X_test, bedroom_ratio_test])
    
    print(f"  ✅ Added 1 new feature(s)")
    print(f"  ✅ New shape: {X_train_new.shape}")
    
    # 저장
    output_dir = "/tmp/featured"
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(f"{output_dir}/X_train.npy", X_train_new)
    np.save(f"{output_dir}/X_test.npy", X_test_new)
    
    # y 데이터 복사
    import shutil
    shutil.copy(f"{data_dir}/y_train.npy", f"{output_dir}/y_train.npy")
    shutil.copy(f"{data_dir}/y_test.npy", f"{output_dir}/y_test.npy")
    
    return output_dir


# ============================================================
# TODO 4: 모델 학습 + MLflow 컴포넌트
# ============================================================

@create_component_from_func
def train_model(
    data_dir: str,
    mlflow_tracking_uri: str,
    experiment_name: str,
    n_estimators: int = 100,
    max_depth: int = 10
) -> str:
    """
    모델 학습 및 MLflow에 기록
    
    Args:
        data_dir: 학습 데이터 디렉토리
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: 실험 이름
        n_estimators: RandomForest 트리 개수
        max_depth: RandomForest 최대 깊이
    
    Returns:
        MLflow Run ID
    """
    # TODO: MLflow 연동 코드를 완성하세요!
    
    import numpy as np
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    import os
    
    print("=" * 50)
    print("  Step 4: Train Model")
    print("=" * 50)
    
    # MLflow 설정
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    # 데이터 로드
    X_train = np.load(f"{data_dir}/X_train.npy")
    X_test = np.load(f"{data_dir}/X_test.npy")
    y_train = np.load(f"{data_dir}/y_train.npy")
    y_test = np.load(f"{data_dir}/y_test.npy")
    
    # TODO: MLflow Run 시작 및 기록
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        
        # TODO: 파라미터 기록
        # 힌트: mlflow.log_params({...})
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
        
        # TODO: 메트릭 기록
        # 힌트: mlflow.log_metrics({...})
        mlflow.log_metrics({
            "mse": mse,
            "rmse": np.sqrt(mse),
            "r2": r2
        })
        
        # TODO: 모델 저장
        # 힌트: mlflow.sklearn.log_model(...)
        mlflow.sklearn.log_model(model, "model")
        
        print(f"  ✅ R2: {r2:.4f}, RMSE: {np.sqrt(mse):.4f}")
        print(f"  ✅ Run ID: {run_id}")
    
    return run_id


# ============================================================
# (선택) TODO 5: KServe 배포 컴포넌트
# ============================================================

@create_component_from_func
def deploy_model(
    run_id: str,
    model_name: str,
    namespace: str
):
    """
    KServe InferenceService로 모델 배포
    
    Args:
        run_id: MLflow Run ID
        model_name: 배포 모델 이름
        namespace: Kubernetes 네임스페이스
    """
    # TODO: KServe 배포 코드 구현 (선택 과제)
    
    print("=" * 50)
    print("  Step 5: Deploy Model (Optional)")
    print("=" * 50)
    
    # 힌트: kubernetes 라이브러리를 사용하여 InferenceService 생성
    # from kubernetes import client, config
    # config.load_incluster_config()
    # api = client.CustomObjectsApi()
    # api.create_namespaced_custom_object(...)
    
    print(f"  ⚠️  Deployment not implemented yet")
    print(f"  💡 Bonus: Implement KServe deployment for extra points!")


# ============================================================
# 파이프라인 정의
# ============================================================

@dsl.pipeline(
    name='Team Project Pipeline',
    description='California Housing E2E ML Pipeline'
)
def project_pipeline(
    mlflow_tracking_uri: str = "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000",
    experiment_name: str = "team-project",
    model_name: str = "california-model",
    namespace: str = "kubeflow-user01",  # TODO: 자신의 네임스페이스로 변경!
    n_estimators: int = 100,
    max_depth: int = 10
):
    """
    Team Project Pipeline
    
    Args:
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: MLflow 실험 이름
        model_name: 배포 모델 이름
        namespace: Kubernetes 네임스페이스
        n_estimators: RandomForest 트리 개수
        max_depth: RandomForest 최대 깊이
    """
    
    # Step 1: 데이터 로드
    load_task = load_data()
    
    # Step 2: 전처리
    preprocess_task = preprocess(data_path=load_task.output)
    
    # Step 3: 피처 엔지니어링
    feature_task = feature_engineering(data_dir=preprocess_task.output)
    
    # Step 4: 모델 학습 (MLflow)
    train_task = train_model(
        data_dir=feature_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name,
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    
    # Step 5: (선택) KServe 배포
    # deploy_model(
    #     run_id=train_task.output,
    #     model_name=model_name,
    #     namespace=namespace
    # )


# ============================================================
# 메인 실행
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  🎯 Team Project: E2E ML Pipeline")
    print("=" * 60)
    
    # 파이프라인 컴파일
    print("\n[1] Compiling Pipeline...")
    
    pipeline_file = 'project_pipeline.yaml'
    compiler.Compiler().compile(
        pipeline_func=project_pipeline,
        package_path=pipeline_file
    )
    print(f"  ✅ Compiled: {pipeline_file}")
    
    # 파이프라인 실행
    print("\n[2] Submitting Pipeline...")
    
    try:
        client = kfp.Client()
        
        # TODO: 네임스페이스를 자신의 것으로 변경!
        run = client.create_run_from_pipeline_func(
            project_pipeline,
            arguments={
                'experiment_name': 'team-XX-project',  # TODO: 팀 번호로 변경
                'namespace': 'kubeflow-userXX',        # TODO: 자신의 네임스페이스
                'n_estimators': 100,
                'max_depth': 10
            },
            experiment_name='team-project-experiment',
            run_name='team-XX-run-001'  # TODO: 팀 번호로 변경
        )
        
        print(f"  ✅ Pipeline submitted!")
        print(f"  ✅ Run ID: {run.run_id}")
        print("\n💡 Check Kubeflow Dashboard → Runs")
        
    except Exception as e:
        print(f"  ⚠️  Could not submit: {e}")
        print(f"\n✅ YAML created: {pipeline_file}")
        print("   Upload via Kubeflow UI")
    
    print("\n" + "=" * 60)
    print("  Good luck with your project! 🚀")
    print("=" * 60)
