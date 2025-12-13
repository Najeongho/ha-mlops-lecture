#!/bin/bash
# ============================================================
# setup-env.sh - MLOps Training 환경 변수 설정
# ============================================================
# 
# 사용법:
#   source scripts/setup-env.sh
#
# 사전 요구사항:
#   - AWS CLI 설치 및 자격 증명 설정
#   - kubectl 설치 및 EKS 클러스터 연결
#
# ============================================================

# ============================================================
# 사용자 번호 설정 (각자 수정!)
# ============================================================
# ⚠️ 본인의 번호로 변경하세요! (예: 01, 02, ..., 15, 20)
export USER_NUM="${USER_NUM:-01}"

# ============================================================
# 공통 설정 (수정 불필요)
# ============================================================

# Kubernetes 설정
export NAMESPACE="kubeflow-user${USER_NUM}"
export CLUSTER_NAME="mlops-training-cluster"

# AWS 설정
export AWS_REGION="ap-northeast-2"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")

# ============================================================
# S3 버킷 설정 (사용자별 단일 버킷)
# ============================================================
export S3_BUCKET="mlops-training-user${USER_NUM}"

# Data Lake 레이어 (S3 내부 경로)
export BRONZE_LAYER="s3://${S3_BUCKET}/raw"
export SILVER_LAYER="s3://${S3_BUCKET}/processed"
export GOLD_LAYER="s3://${S3_BUCKET}/curated"

# MLflow 아티팩트 경로
export MLFLOW_ARTIFACT_PATH="s3://${S3_BUCKET}/mlflow-artifacts"

# ============================================================
# ECR 설정 (사용자별 레포지토리)
# ============================================================
export ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# 사용자별 ECR 레포지토리
export ECR_IRIS_API_REPO="mlops-training/user${USER_NUM}/iris-api"

# 공용 ECR 레포지토리 (california-housing 모델)
export ECR_CALIFORNIA_HOUSING_REPO="ml-model-california-housing"

# 전체 ECR 이미지 경로
export ECR_IRIS_API_IMAGE="${ECR_REGISTRY}/${ECR_IRIS_API_REPO}"
export ECR_CALIFORNIA_HOUSING_IMAGE="${ECR_REGISTRY}/${ECR_CALIFORNIA_HOUSING_REPO}"

# ============================================================
# MLflow 설정
# ============================================================
export MLFLOW_TRACKING_URI="http://mlflow-server-service.mlflow-system.svc.cluster.local:5000"
export MLFLOW_S3_ENDPOINT_URL="http://minio-service.kubeflow.svc:9000"

# ============================================================
# Kubeflow 설정
# ============================================================
export KF_PIPELINES_ENDPOINT="http://ml-pipeline-ui.kubeflow.svc.cluster.local"

# ============================================================
# 설정 확인 출력
# ============================================================

echo "============================================================"
echo "  MLOps Training Environment Variables"
echo "============================================================"
echo ""
echo "  👤 User Number:     ${USER_NUM}"
echo "  📁 Namespace:       ${NAMESPACE}"
echo "  ☁️  AWS Region:      ${AWS_REGION}"
echo "  🆔 AWS Account:     ${AWS_ACCOUNT_ID}"
echo ""
echo "  📦 S3 Bucket:       s3://${S3_BUCKET}"
echo "     - Bronze Layer: ${BRONZE_LAYER}"
echo "     - Silver Layer: ${SILVER_LAYER}"
echo "     - Gold Layer:   ${GOLD_LAYER}"
echo "     - MLflow:       ${MLFLOW_ARTIFACT_PATH}"
echo ""
echo "  🐳 ECR Registry:    ${ECR_REGISTRY}"
echo "     - iris-api:      ${ECR_IRIS_API_REPO}"
echo "     - california:    ${ECR_CALIFORNIA_HOUSING_REPO} (공용)"
echo ""
echo "  📊 MLflow URI:      ${MLFLOW_TRACKING_URI}"
echo ""
echo "============================================================"
echo "  ✅ Environment setup complete!"
echo "============================================================"

# ============================================================
# 환경 변수 검증
# ============================================================
if [[ "${AWS_ACCOUNT_ID}" == "unknown" ]]; then
    echo ""
    echo "⚠️  경고: AWS 자격 증명을 확인할 수 없습니다."
    echo "   다음 명령어로 AWS CLI를 설정하세요:"
    echo "   aws configure"
fi
