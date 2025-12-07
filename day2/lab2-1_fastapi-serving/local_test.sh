#!/bin/bash
# Lab 2-1: 로컬 개발 환경 테스트 스크립트
# ========================================

set -e

echo "============================================================"
echo "  Lab 2-1: Local Development Test"
echo "============================================================"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: 가상환경 확인
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1: 가상환경 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  가상환경이 없습니다. 생성합니다...${NC}"
    python -m venv .venv
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
else
    echo -e "${GREEN}✅ 가상환경이 이미 존재합니다${NC}"
fi

echo ""
echo "가상환경 활성화:"
echo "  source .venv/bin/activate  # macOS/Linux"
echo "  .venv\\Scripts\\activate   # Windows"
echo ""

# 가상환경이 활성화되어 있는지 확인
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  가상환경이 활성화되지 않았습니다.${NC}"
    echo "다음 명령어로 활성화하세요:"
    echo "  source .venv/bin/activate"
    echo ""
    read -p "활성화 후 Enter를 눌러 계속하세요..."
fi

# Step 2: 의존성 설치
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 2: 의존성 설치"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pip install -q -r requirements.txt
echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
echo ""

# Step 3: 모델 학습
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 3: 모델 학습"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "model.joblib" ]; then
    echo "model.joblib 파일이 없습니다. 모델을 학습합니다..."
    python train_model.py
else
    echo -e "${GREEN}✅ model.joblib 파일이 이미 존재합니다${NC}"
    echo ""
    read -p "모델을 다시 학습하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python train_model.py
    fi
fi

echo ""

# Step 4: FastAPI 서버 실행
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 4: FastAPI 서버 실행"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}FastAPI 서버를 시작합니다...${NC}"
echo ""
echo "서버가 시작되면 다음을 테스트하세요:"
echo ""
echo "  1. Health Check:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  2. Swagger UI (브라우저):"
echo "     http://localhost:8000/docs"
echo ""
echo "  3. API 테스트 스크립트 (다른 터미널):"
echo "     ./tests/test_api.sh"
echo ""
echo "  4. 서버 종료: Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# uvicorn 실행
uvicorn app.main:app --reload --port 8000
