"""
Lab 2-3: 모델 준비 및 S3 업로드 스크립트
========================================

KServe 배포를 위해 학습된 모델을 S3에 업로드합니다.

사용법:
    python prepare_model.py [--bucket mlops-training-models] [--model-name california-model]
"""

import argparse
import os
import joblib
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score


def train_model():
    """모델 학습"""
    print("=" * 60)
    print("  Step 1: 모델 학습")
    print("=" * 60)
    
    # 데이터 로드
    print("\n  데이터 로드 중...")
    data = fetch_california_housing()
    X, y = data.data, data.target
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"  - 학습 샘플: {len(X_train)}")
    print(f"  - 테스트 샘플: {len(X_test)}")
    
    # 모델 학습
    print("\n  모델 학습 중...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # 평가
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\n  ✅ 모델 학습 완료!")
    print(f"  - R2 Score: {r2:.4f}")
    print(f"  - RMSE: {rmse:.4f}")
    
    return model


def save_model_local(model, output_dir: str = "model"):
    """모델을 로컬에 저장"""
    print("\n" + "=" * 60)
    print("  Step 2: 모델 로컬 저장")
    print("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "model.joblib")
    joblib.dump(model, model_path)
    
    print(f"\n  ✅ 모델 저장: {model_path}")
    print(f"  - 파일 크기: {os.path.getsize(model_path) / 1024:.1f} KB")
    
    return model_path


def upload_to_s3(local_path: str, bucket: str, model_name: str):
    """S3에 모델 업로드"""
    print("\n" + "=" * 60)
    print("  Step 3: S3 업로드")
    print("=" * 60)
    
    try:
        import boto3
        
        s3_client = boto3.client('s3')
        
        # S3 경로
        s3_key = f"{model_name}/model/model.joblib"
        
        print(f"\n  업로드 중...")
        print(f"  - 소스: {local_path}")
        print(f"  - 대상: s3://{bucket}/{s3_key}")
        
        s3_client.upload_file(local_path, bucket, s3_key)
        
        print(f"\n  ✅ S3 업로드 완료!")
        
        # 업로드 확인
        response = s3_client.head_object(Bucket=bucket, Key=s3_key)
        print(f"  - 파일 크기: {response['ContentLength'] / 1024:.1f} KB")
        print(f"  - Last Modified: {response['LastModified']}")
        
        return f"s3://{bucket}/{model_name}/model"
        
    except ImportError:
        print("\n  ❌ boto3가 설치되지 않았습니다.")
        print("     pip install boto3")
        return None
    except Exception as e:
        print(f"\n  ❌ S3 업로드 실패: {e}")
        print("\n  💡 AWS 자격 증명을 확인하세요:")
        print("     aws configure")
        return None


def generate_inference_yaml(model_name: str, s3_uri: str, namespace: str):
    """InferenceService YAML 생성"""
    print("\n" + "=" * 60)
    print("  Step 4: InferenceService YAML 생성")
    print("=" * 60)
    
    yaml_content = f"""apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: {model_name}
  namespace: {namespace}
  annotations:
    autoscaling.knative.dev/minScale: "1"
    autoscaling.knative.dev/maxScale: "3"
spec:
  predictor:
    sklearn:
      storageUri: "{s3_uri}"
      resources:
        requests:
          cpu: "100m"
          memory: "256Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
"""
    
    yaml_path = f"inference-service-{model_name}.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    
    print(f"\n  ✅ YAML 파일 생성: {yaml_path}")
    print(f"\n  배포 명령어:")
    print(f"  kubectl apply -f {yaml_path}")
    
    return yaml_path


def main():
    parser = argparse.ArgumentParser(description='KServe용 모델 준비 및 S3 업로드')
    parser.add_argument('--bucket', type=str, default='mlops-training-models',
                        help='S3 버킷 이름')
    parser.add_argument('--model-name', type=str, default='california-model',
                        help='모델 이름')
    parser.add_argument('--namespace', type=str, default='kubeflow-user01',
                        help='Kubernetes 네임스페이스')
    parser.add_argument('--skip-upload', action='store_true',
                        help='S3 업로드 건너뛰기')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Lab 2-3: KServe 모델 준비")
    print("=" * 60)
    print(f"\n  Bucket: {args.bucket}")
    print(f"  Model Name: {args.model_name}")
    print(f"  Namespace: {args.namespace}")
    
    # Step 1: 모델 학습
    model = train_model()
    
    # Step 2: 로컬 저장
    model_path = save_model_local(model, output_dir="model")
    
    # Step 3: S3 업로드
    if not args.skip_upload:
        s3_uri = upload_to_s3(model_path, args.bucket, args.model_name)
        
        if s3_uri:
            # Step 4: YAML 생성
            generate_inference_yaml(args.model_name, s3_uri, args.namespace)
    else:
        print("\n  ⏭️  S3 업로드 건너뜀 (--skip-upload)")
        s3_uri = f"s3://{args.bucket}/{args.model_name}/model"
        generate_inference_yaml(args.model_name, s3_uri, args.namespace)
    
    # 완료
    print("\n" + "=" * 60)
    print("  ✅ 모델 준비 완료!")
    print("=" * 60)
    print(f"\n  다음 단계:")
    print(f"  1. kubectl apply -f inference-service-{args.model_name}.yaml")
    print(f"  2. kubectl get inferenceservice -n {args.namespace}")
    print(f"  3. ./test_inference.sh")
    print("")


if __name__ == '__main__':
    main()
