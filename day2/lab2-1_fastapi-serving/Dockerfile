# Lab 2-1: FastAPI Model Serving Dockerfile
# ============================================
# 
# ✅ 수정: 멀티 플랫폼 지원 (AMD64/ARM64)
# EKS는 AMD64를 사용하므로 명시적 플랫폼 지정 필요

FROM --platform=linux/amd64 python:3.9-slim

# 메타데이터
LABEL maintainer="MLOps Training"
LABEL description="Iris Classification API with FastAPI"
LABEL version="1.0.1"
LABEL platform="linux/amd64"

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (필요한 경우)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app/ ./app/
COPY model.joblib .

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 포트 노출
EXPOSE 8000

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
