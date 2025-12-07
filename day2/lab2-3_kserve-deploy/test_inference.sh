#!/bin/bash
# Lab 2-3: KServe Inference Test Script
# ======================================

API_URL="${API_URL:-http://localhost:8080}"
MODEL_NAME="${MODEL_NAME:-california-model}"

echo "============================================================"
echo "  KServe Inference Test"
echo "  API URL: ${API_URL}"
echo "  Model: ${MODEL_NAME}"
echo "============================================================"

# 테스트 1: 단일 예측
echo ""
echo "[Test 1] Single Prediction"
echo "  POST ${API_URL}/v1/models/${MODEL_NAME}:predict"
curl -s -X POST "${API_URL}/v1/models/${MODEL_NAME}:predict" \
    -H "Content-Type: application/json" \
    -d '{
        "instances": [
            [8.3252, 41.0, 6.984, 1.024, 322.0, 2.556, 37.88, -122.23]
        ]
    }' | python3 -m json.tool
echo ""

# 테스트 2: 배치 예측
echo "[Test 2] Batch Prediction (3 samples)"
echo "  POST ${API_URL}/v1/models/${MODEL_NAME}:predict"
curl -s -X POST "${API_URL}/v1/models/${MODEL_NAME}:predict" \
    -H "Content-Type: application/json" \
    -d '{
        "instances": [
            [8.3252, 41.0, 6.984, 1.024, 322.0, 2.556, 37.88, -122.23],
            [3.5, 30.0, 5.0, 1.0, 1000.0, 3.0, 34.0, -118.0],
            [5.0, 25.0, 6.0, 1.2, 500.0, 2.5, 36.0, -120.0]
        ]
    }' | python3 -m json.tool
echo ""

# 테스트 3: 다양한 주택 가격 예측
echo "[Test 3] Various Housing Predictions"

# 저가 주택
echo "  Low-value area:"
curl -s -X POST "${API_URL}/v1/models/${MODEL_NAME}:predict" \
    -H "Content-Type: application/json" \
    -d '{"instances": [[2.0, 40.0, 4.0, 1.0, 2000.0, 4.0, 33.0, -117.0]]}' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'    Predicted: ${d[\"predictions\"][0]:.2f} (\$100k)')"

# 중가 주택
echo "  Mid-value area:"
curl -s -X POST "${API_URL}/v1/models/${MODEL_NAME}:predict" \
    -H "Content-Type: application/json" \
    -d '{"instances": [[5.0, 30.0, 6.0, 1.1, 1000.0, 2.5, 35.0, -119.0]]}' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'    Predicted: ${d[\"predictions\"][0]:.2f} (\$100k)')"

# 고가 주택
echo "  High-value area:"
curl -s -X POST "${API_URL}/v1/models/${MODEL_NAME}:predict" \
    -H "Content-Type: application/json" \
    -d '{"instances": [[10.0, 20.0, 8.0, 1.5, 300.0, 2.0, 37.5, -122.3]]}' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'    Predicted: ${d[\"predictions\"][0]:.2f} (\$100k)')"

echo ""
echo "============================================================"
echo "  ✅ All tests completed!"
echo "============================================================"
echo ""
echo "💡 Feature order: MedInc, HouseAge, AveRooms, AveBedrms,"
echo "   Population, AveOccup, Latitude, Longitude"
echo ""
