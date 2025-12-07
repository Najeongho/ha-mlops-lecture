"""
Lab 2-1: 모델 학습 및 저장
==========================

Iris 데이터셋으로 RandomForest 모델을 학습하고 저장합니다.
"""

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


def train_and_save_model():
    """
    Iris 분류 모델을 학습하고 저장합니다.
    """
    print("=" * 60)
    print("  Training Iris Classification Model")
    print("=" * 60)
    
    # 데이터 로드
    print("\n[1/4] Loading Iris dataset...")
    iris = load_iris()
    X, y = iris.data, iris.target
    
    print(f"  - Samples: {len(X)}")
    print(f"  - Features: {X.shape[1]}")
    print(f"  - Classes: {list(iris.target_names)}")
    
    # Train/Test 분할
    print("\n[2/4] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"  - Train samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    
    # 모델 학습
    print("\n[3/4] Training RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # 평가
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"  - Accuracy: {accuracy:.4f}")
    
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))
    
    # 모델 저장
    print("[4/4] Saving model...")
    model_path = 'model.joblib'
    joblib.dump(model, model_path)
    print(f"  ✅ Model saved: {model_path}")
    
    # 저장된 모델 확인
    print("\n[Test] Loading saved model...")
    loaded_model = joblib.load(model_path)
    test_sample = [[5.1, 3.5, 1.4, 0.2]]  # setosa
    pred = loaded_model.predict(test_sample)[0]
    proba = loaded_model.predict_proba(test_sample)[0]
    
    print(f"  - Test input: {test_sample[0]}")
    print(f"  - Prediction: {iris.target_names[pred]} (class {pred})")
    print(f"  - Probability: {max(proba):.4f}")
    
    print("\n" + "=" * 60)
    print("  ✅ Model training complete!")
    print("=" * 60)
    
    return model


if __name__ == '__main__':
    train_and_save_model()
