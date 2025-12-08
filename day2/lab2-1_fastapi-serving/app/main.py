"""
Lab 2-1: FastAPI 모델 서빙
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import joblib
import numpy as np
from pathlib import Path

app = FastAPI(title="Iris Classification API", version="1.0.0")

# 모델 로드
MODEL_PATH = Path(__file__).parent.parent / "model.joblib"
try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOADED = True
except:
    model = None
    MODEL_LOADED = False

IRIS_SPECIES = {0: "setosa", 1: "versicolor", 2: "virginica"}

class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., ge=0, le=10)
    sepal_width: float = Field(..., ge=0, le=10)
    petal_length: float = Field(..., ge=0, le=10)
    petal_width: float = Field(..., ge=0, le=10)

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float

@app.get("/")
async def root():
    return {"message": "Iris Classification API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy" if MODEL_LOADED else "unhealthy", "model_loaded": MODEL_LOADED}

@app.post("/predict", response_model=PredictionResponse)
async def predict(features: IrisFeatures):
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    input_data = np.array([[features.sepal_length, features.sepal_width, 
                            features.petal_length, features.petal_width]])
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    
    return PredictionResponse(
        prediction=IRIS_SPECIES[prediction],
        confidence=float(probabilities[prediction])
    )

@app.post("/predict/batch")
async def predict_batch(features_list: List[IrisFeatures]):
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    input_data = np.array([[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]
                           for f in features_list])
    predictions = model.predict(input_data)
    probabilities = model.predict_proba(input_data)
    
    results = []
    for pred, probs in zip(predictions, probabilities):
        results.append(PredictionResponse(
            prediction=IRIS_SPECIES[pred],
            confidence=float(probs[pred])
        ))
    
    return {"predictions": results}
