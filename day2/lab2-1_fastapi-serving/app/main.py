"""
Lab 2-1: FastAPI Model Serving Application
==========================================

Iris 분류 모델을 REST API로 서빙하는 FastAPI 애플리케이션
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
from typing import List

# ============================================================
# FastAPI 앱 초기화
# ============================================================

app = FastAPI(
    title="Iris Classification API",
    description="Iris 꽃 분류를 위한 ML 모델 API",
    version="1.0.0"
)

# 모델 로드
try:
    model = joblib.load('model.joblib')
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Failed to load model: {e}")
    model = None

# 클래스 이름
CLASS_NAMES = ['setosa', 'versicolor', 'virginica']


# ============================================================
# Pydantic 스키마 정의
# ============================================================

class IrisFeatures(BaseModel):
    """Iris 꽃 피처 입력 스키마"""
    sepal_length: float = Field(..., ge=0, le=10, description="꽃받침 길이 (cm)")
    sepal_width: float = Field(..., ge=0, le=10, description="꽃받침 너비 (cm)")
    petal_length: float = Field(..., ge=0, le=10, description="꽃잎 길이 (cm)")
    petal_width: float = Field(..., ge=0, le=10, description="꽃잎 너비 (cm)")
    
    class Config:
        schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }


class PredictionResponse(BaseModel):
    """예측 결과 응답 스키마"""
    prediction: int = Field(..., description="예측된 클래스 번호")
    class_name: str = Field(..., description="예측된 클래스 이름")
    probability: float = Field(..., description="예측 확률")
    probabilities: List[float] = Field(..., description="각 클래스별 확률")


class HealthResponse(BaseModel):
    """헬스체크 응답 스키마"""
    status: str
    model_loaded: bool


# ============================================================
# API 엔드포인트
# ============================================================

@app.get("/", tags=["Root"])
def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Iris Classification API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """헬스체크 엔드포인트"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: IrisFeatures):
    """
    Iris 꽃 분류 예측
    
    - **sepal_length**: 꽃받침 길이 (cm)
    - **sepal_width**: 꽃받침 너비 (cm)
    - **petal_length**: 꽃잎 길이 (cm)
    - **petal_width**: 꽃잎 너비 (cm)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # 입력 데이터 변환
    X = np.array([[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width
    ]])
    
    # 예측
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    
    return PredictionResponse(
        prediction=int(prediction),
        class_name=CLASS_NAMES[prediction],
        probability=float(max(probabilities)),
        probabilities=[float(p) for p in probabilities]
    )


@app.post("/predict/batch", tags=["Prediction"])
def predict_batch(features_list: List[IrisFeatures]):
    """
    배치 예측 엔드포인트
    
    여러 샘플을 한 번에 예측합니다.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # 입력 데이터 변환
    X = np.array([
        [f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]
        for f in features_list
    ])
    
    # 예측
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    results = []
    for i, (pred, proba) in enumerate(zip(predictions, probabilities)):
        results.append({
            "index": i,
            "prediction": int(pred),
            "class_name": CLASS_NAMES[pred],
            "probability": float(max(proba))
        })
    
    return {"predictions": results, "count": len(results)}


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
