"""
Lab 3-2: 모델 배포 컴포넌트
==========================

KServe InferenceService로 모델을 배포하는 컴포넌트
"""

from kfp.components import create_component_from_func


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
    import os
    import time
    
    print("=" * 50)
    print("  Component: Deploy Model")
    print("=" * 50)
    
    # Kubernetes 설정
    print("\n  🔧 Kubernetes 설정 중...")
    try:
        config.load_incluster_config()
        print("  ✅ In-cluster config 로드됨")
    except:
        config.load_kube_config()
        print("  ✅ Kube config 로드됨")
    
    # InferenceService 정의
    model_uri = f"s3://mlflow-artifacts/{run_id}/artifacts/model"
    
    print(f"\n  📦 배포 정보:")
    print(f"     - Model Name: {model_name}")
    print(f"     - Namespace: {namespace}")
    print(f"     - Model URI: {model_uri}")
    print(f"     - Run ID: {run_id}")
    
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
                "autoscaling.knative.dev/minScale": "1",
                "autoscaling.knative.dev/maxScale": "3"
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
    
    # 배포
    api = client.CustomObjectsApi()
    
    # 기존 리소스 삭제 (있으면)
    print("\n  🗑️ 기존 InferenceService 확인...")
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        print(f"  ⚠️ 기존 InferenceService '{model_name}' 삭제됨")
        time.sleep(5)  # 삭제 완료 대기
    except ApiException as e:
        if e.status == 404:
            print("  ✅ 기존 InferenceService 없음")
        else:
            raise
    
    # 새로 생성
    print("\n  🚀 InferenceService 생성 중...")
    try:
        result = api.create_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            body=isvc
        )
        print(f"  ✅ InferenceService 생성됨: {model_name}")
        
    except ApiException as e:
        print(f"  ❌ 배포 실패: {e.reason}")
        raise
    
    # 상태 확인 (간단히)
    print("\n  ⏳ 배포 상태 확인 중... (최대 60초 대기)")
    for i in range(6):
        time.sleep(10)
        try:
            isvc_status = api.get_namespaced_custom_object(
                group="serving.kserve.io",
                version="v1beta1",
                namespace=namespace,
                plural="inferenceservices",
                name=model_name
            )
            
            conditions = isvc_status.get("status", {}).get("conditions", [])
            ready_condition = next(
                (c for c in conditions if c.get("type") == "Ready"),
                None
            )
            
            if ready_condition and ready_condition.get("status") == "True":
                print(f"  ✅ InferenceService READY!")
                break
            else:
                status = ready_condition.get("status", "Unknown") if ready_condition else "Unknown"
                print(f"  ⏳ Status: {status} ({(i+1)*10}s)")
                
        except Exception as e:
            print(f"  ⚠️ 상태 확인 실패: {e}")
    
    # 엔드포인트 정보
    print(f"\n  📡 엔드포인트:")
    print(f"     http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict")
    
    print(f"\n  ✅ 배포 완료!")


# 컴포넌트 직접 실행 시
if __name__ == "__main__":
    # 테스트
    deploy_model.python_func(
        run_id="test-run-id",
        model_name="test-model",
        namespace="kubeflow-user01",
        mlflow_tracking_uri="http://localhost:5000"
    )
