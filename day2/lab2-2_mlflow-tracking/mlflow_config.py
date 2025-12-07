"""
Lab 2-2: MLflow Configuration
==============================

MLflow 서버 연결 설정 모듈
"""

import os


def configure_mlflow():
    """
    MLflow 환경 변수를 설정합니다.
    
    Kubeflow 환경에서 실행할 때 사용합니다.
    """
    
    # MLflow Tracking Server URI
    os.environ['MLFLOW_TRACKING_URI'] = os.getenv(
        'MLFLOW_TRACKING_URI',
        'http://mlflow-server-service.mlflow-system.svc.cluster.local:5000'
    )
    
    # S3/MinIO 설정 (아티팩트 저장용)
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = os.getenv(
        'MLFLOW_S3_ENDPOINT_URL',
        'http://minio-service.kubeflow.svc:9000'
    )
    
    # MinIO 자격 증명
    os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID', 'minio')
    os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY', 'minio123')
    
    print("=" * 60)
    print("  MLflow Configuration")
    print("=" * 60)
    print(f"  Tracking URI: {os.environ['MLFLOW_TRACKING_URI']}")
    print(f"  S3 Endpoint:  {os.environ['MLFLOW_S3_ENDPOINT_URL']}")
    print("=" * 60)


def configure_mlflow_local():
    """
    로컬 MLflow 서버에 연결합니다.
    
    로컬에서 테스트할 때 사용합니다 (port-forward 필요).
    """
    
    os.environ['MLFLOW_TRACKING_URI'] = 'http://localhost:5000'
    
    print("=" * 60)
    print("  MLflow Configuration (Local)")
    print("=" * 60)
    print(f"  Tracking URI: {os.environ['MLFLOW_TRACKING_URI']}")
    print("=" * 60)


if __name__ == '__main__':
    # 기본 설정 적용
    configure_mlflow()
    
    # 연결 테스트
    import mlflow
    
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    
    print("\n[Test] Connecting to MLflow server...")
    try:
        experiments = mlflow.search_experiments()
        print(f"  ✅ Connected! Found {len(experiments)} experiments")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
