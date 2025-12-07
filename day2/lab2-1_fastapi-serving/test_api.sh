#!/bin/bash
# Lab 2-1: API 테스트 스크립트
# ============================

API_URL="${API_URL:-http://localhost:8080}"

echo "============================================================"
echo "  Iris API Test Script"
echo "  API URL: ${API_URL}"
echo "============================================================"

# 테스트 1: 헬스체크
echo ""
echo "[Test 1] Health Check"
echo "  GET ${API_URL}/health"
curl -s ${API_URL}/health | python3 -m json.tool
echo ""

# 테스트 2: Setosa 예측
echo "[Test 2] Predict Setosa"
echo "  POST ${API_URL}/predict"
curl -s -X POST ${API_URL}/predict \
    -H "Content-Type: application/json" \
    -d '{
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }' | python3 -m json.tool
echo ""

# 테스트 3: Versicolor 예측
echo "[Test 3] Predict Versicolor"
echo "  POST ${API_URL}/predict"
curl -s -X POST ${API_URL}/predict \
    -H "Content-Type: application/json" \
    -d '{
        "sepal_length": 6.0,
        "sepal_width": 2.7,
        "petal_length": 4.2,
        "petal_width": 1.3
    }' | python3 -m json.tool
echo ""

# 테스트 4: Virginica 예측
echo "[Test 4] Predict Virginica"
echo "  POST ${API_URL}/predict"
curl -s -X POST ${API_URL}/predict \
    -H "Content-Type: application/json" \
    -d '{
        "sepal_length": 6.3,
        "sepal_width": 2.9,
        "petal_length": 5.6,
        "petal_width": 1.8
    }' | python3 -m json.tool
echo ""

# 테스트 5: 배치 예측
echo "[Test 5] Batch Prediction"
echo "  POST ${API_URL}/predict/batch"
curl -s -X POST ${API_URL}/predict/batch \
    -H "Content-Type: application/json" \
    -d '[
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        {"sepal_length": 6.0, "sepal_width": 2.7, "petal_length": 4.2, "petal_width": 1.3},
        {"sepal_length": 6.3, "sepal_width": 2.9, "petal_length": 5.6, "petal_width": 1.8}
    ]' | python3 -m json.tool
echo ""

echo "============================================================"
echo "  ✅ All tests completed!"
echo "============================================================"
echo ""
echo "💡 Swagger UI: ${API_URL}/docs"
echo ""
