#!/bin/bash
# Lab 2-1: API 통합 테스트 스크립트
# ====================================

API_URL="${API_URL:-http://localhost:8000}"

echo "============================================================"
echo "  Iris API Integration Test"
echo "  API URL: ${API_URL}"
echo "============================================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 결과 카운터
PASSED=0
FAILED=0

# 테스트 함수
test_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Test: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $method $API_URL$endpoint"
    
    if [ -n "$data" ]; then
        echo "  Data: $data"
    fi
    
    # HTTP 요청 실행
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # HTTP 상태 코드 추출
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # 결과 출력
    echo ""
    echo "  Response (HTTP $http_code):"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    
    # 검증
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "  ${GREEN}✅ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "  ${RED}❌ FAILED - Expected $expected_status, got $http_code${NC}"
        ((FAILED++))
    fi
}

# 테스트 1: Health Check
test_endpoint \
    "Health Check" \
    "GET" \
    "/health" \
    "" \
    "200"

# 테스트 2: Predict Setosa
test_endpoint \
    "Predict Setosa (expected class 0)" \
    "POST" \
    "/predict" \
    '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}' \
    "200"

# 테스트 3: Predict Versicolor
test_endpoint \
    "Predict Versicolor (expected class 1)" \
    "POST" \
    "/predict" \
    '{"sepal_length": 6.0, "sepal_width": 2.7, "petal_length": 4.2, "petal_width": 1.3}' \
    "200"

# 테스트 4: Predict Virginica
test_endpoint \
    "Predict Virginica (expected class 2)" \
    "POST" \
    "/predict" \
    '{"sepal_length": 6.3, "sepal_width": 2.9, "petal_length": 5.6, "petal_width": 1.8}' \
    "200"

# 테스트 5: Batch Prediction
test_endpoint \
    "Batch Prediction (3 samples)" \
    "POST" \
    "/predict/batch" \
    '[
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        {"sepal_length": 6.0, "sepal_width": 2.7, "petal_length": 4.2, "petal_width": 1.3},
        {"sepal_length": 6.3, "sepal_width": 2.9, "petal_length": 5.6, "petal_width": 1.8}
    ]' \
    "200"

# 테스트 6: Invalid Input (negative value)
test_endpoint \
    "Invalid Input - Negative Value (expected 422)" \
    "POST" \
    "/predict" \
    '{"sepal_length": -1.0, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}' \
    "422"

# 테스트 7: Invalid Input (missing field)
test_endpoint \
    "Invalid Input - Missing Field (expected 422)" \
    "POST" \
    "/predict" \
    '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4}' \
    "422"

# 최종 결과
echo ""
echo "============================================================"
echo "  Test Results Summary"
echo "============================================================"
echo ""
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo "  Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "💡 Swagger UI: $API_URL/docs"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    exit 1
fi
