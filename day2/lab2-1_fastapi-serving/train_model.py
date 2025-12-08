#!/usr/bin/env python3
"""
Lab 2-1: Iris 분류 모델 학습
"""

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

print("="*60)
print("  Iris 분류 모델 학습")
print("="*60)

# 데이터 로드
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

print(f"\n학습 데이터: {len(X_train)} samples")
print(f"테스트 데이터: {len(X_test)} samples\n")

# 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 평가
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"정확도: {accuracy:.4f}\n")

# 저장
joblib.dump(model, "model.joblib")
print("✅ 모델 저장 완료: model.joblib")
print("="*60)
