#!/bin/bash
# ============================================================
# run_pipeline.sh - E2E Pipeline 실행 스크립트
# ============================================================
#
# 사용법:
#   ./run_pipeline.sh [namespace]
#
# 예시:
#   ./run_pipeline.sh kubeflow-user01
# ============================================================

set -e

# 환경 변수
NAMESPACE="${1:-${NAMESPACE:-kubeflow-user01}}"
EXPERIMENT_NAME="${EXPERIMENT_NAME:-e2e-experiment}"
RUN_NAME="${RUN_NAME:-e2e-run-$(date +%Y%m%d-%H%M%S)}"

echo "============================================================"
echo "  E2E Pipeline 실행"
echo "============================================================"
echo ""
echo "  Namespace: ${NAMESPACE}"
echo "  Experiment: ${EXPERIMENT_NAME}"
echo "  Run Name: ${RUN_NAME}"
echo ""

# Step 1: 파이프라인 컴파일
echo "[Step 1] 파이프라인 컴파일..."
python e2e_pipeline.py

if [ ! -f "e2e_pipeline.yaml" ]; then
    echo "  ❌ 컴파일 실패: e2e_pipeline.yaml 파일이 생성되지 않았습니다."
    exit 1
fi
echo "  ✅ 컴파일 완료: e2e_pipeline.yaml"

# Step 2: 파이프라인 업로드 및 실행
echo ""
echo "[Step 2] 파이프라인 실행..."
echo ""
echo "  💡 Kubeflow UI에서 실행하려면:"
echo "     1. http://localhost:8080 접속"
echo "     2. Pipelines → Upload Pipeline"
echo "     3. e2e_pipeline.yaml 업로드"
echo "     4. Create Run → 파라미터 입력:"
echo "        - namespace: ${NAMESPACE}"
echo "        - experiment_name: ${EXPERIMENT_NAME}"
echo "     5. Start 클릭"
echo ""
echo "  또는 Python 스크립트로 실행:"
echo ""
echo "============================================================"

# Python으로 실행 시도
python << EOF
import kfp

try:
    client = kfp.Client()
    print(f"  ✅ KFP Client 연결됨")
    print(f"     Host: {client._host}")
    
    # 파이프라인 업로드
    pipeline = client.upload_pipeline(
        pipeline_package_path='e2e_pipeline.yaml',
        pipeline_name='e2e-ml-pipeline'
    )
    print(f"  ✅ 파이프라인 업로드됨")
    
    # 실험 생성/가져오기
    experiment = client.create_experiment(name='${EXPERIMENT_NAME}')
    print(f"  ✅ 실험: {experiment.name}")
    
    # 파이프라인 실행
    run = client.run_pipeline(
        experiment_id=experiment.id,
        job_name='${RUN_NAME}',
        pipeline_id=pipeline.id,
        params={
            'namespace': '${NAMESPACE}',
            'experiment_name': '${EXPERIMENT_NAME}',
            'model_name': 'california-model',
            'r2_threshold': 0.75
        }
    )
    
    print(f"  ✅ 파이프라인 실행됨!")
    print(f"     Run ID: {run.id}")
    print(f"     Run Name: {run.name}")
    
except Exception as e:
    print(f"  ⚠️ 자동 실행 실패: {e}")
    print(f"     Kubeflow UI에서 수동으로 실행하세요.")
EOF

echo ""
echo "============================================================"
echo "  ✅ 스크립트 완료"
echo "============================================================"
