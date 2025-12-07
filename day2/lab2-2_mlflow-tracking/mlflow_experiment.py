"""
Lab 2-2: MLflow Experiment Tracking
====================================

California Housing 데이터셋으로 실험을 추적하는 예제

실행:
    python mlflow_experiment.py
"""

import mlflow
import mlflow.sklearn
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt
import os

# MLflow 설정 import
from mlflow_config import configure_mlflow


def load_data():
    """California Housing 데이터셋을 로드합니다."""
    print("[1/5] Loading California Housing dataset...")
    
    data = fetch_california_housing()
    X, y = data.data, data.target
    feature_names = data.feature_names
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Test samples: {len(X_test)}")
    print(f"  - Features: {list(feature_names)}")
    
    return X_train, X_test, y_train, y_test, feature_names


def run_experiment(
    X_train, X_test, y_train, y_test, feature_names,
    n_estimators: int,
    max_depth: int,
    run_name: str
):
    """
    단일 실험을 실행하고 MLflow에 기록합니다.
    
    Args:
        n_estimators: 트리 개수
        max_depth: 트리 최대 깊이
        run_name: Run 이름
    """
    print(f"\n[Run] {run_name}")
    print(f"  Parameters: n_estimators={n_estimators}, max_depth={max_depth}")
    
    with mlflow.start_run(run_name=run_name):
        
        # ============================================================
        # 파라미터 기록
        # ============================================================
        mlflow.log_params({
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42,
            "test_size": 0.2
        })
        
        # ============================================================
        # 모델 학습
        # ============================================================
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # ============================================================
        # 예측 및 평가
        # ============================================================
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # ============================================================
        # 메트릭 기록
        # ============================================================
        mlflow.log_metrics({
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        })
        
        print(f"  Metrics: R2={r2:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}")
        
        # ============================================================
        # Feature Importance 시각화
        # ============================================================
        fig, ax = plt.subplots(figsize=(10, 6))
        importance = model.feature_importances_
        indices = np.argsort(importance)[::-1]
        
        ax.barh(range(len(importance)), importance[indices])
        ax.set_yticks(range(len(importance)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.set_xlabel('Feature Importance')
        ax.set_title(f'Feature Importance ({run_name})')
        plt.tight_layout()
        
        # 플롯 저장 및 로깅
        plot_path = f"feature_importance_{run_name}.png"
        plt.savefig(plot_path, dpi=100, bbox_inches='tight')
        mlflow.log_artifact(plot_path)
        plt.close()
        
        # ============================================================
        # 예측 vs 실제 값 시각화
        # ============================================================
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(y_test, y_pred, alpha=0.5)
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax.set_xlabel('Actual')
        ax.set_ylabel('Predicted')
        ax.set_title(f'Predicted vs Actual ({run_name})')
        plt.tight_layout()
        
        scatter_path = f"pred_vs_actual_{run_name}.png"
        plt.savefig(scatter_path, dpi=100, bbox_inches='tight')
        mlflow.log_artifact(scatter_path)
        plt.close()
        
        # ============================================================
        # 모델 저장
        # ============================================================
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name="california-housing-model"
        )
        
        # 로컬 파일 정리
        os.remove(plot_path)
        os.remove(scatter_path)
        
        print(f"  ✅ Run completed! Model registered.")
        
        return r2


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("  Lab 2-2: MLflow Experiment Tracking")
    print("=" * 60)
    
    # MLflow 설정
    configure_mlflow()
    
    # 실험 설정
    experiment_name = "california-housing"
    mlflow.set_experiment(experiment_name)
    print(f"\n[Setup] Experiment: {experiment_name}")
    
    # 데이터 로드
    X_train, X_test, y_train, y_test, feature_names = load_data()
    
    # ============================================================
    # 여러 하이퍼파라미터로 실험 실행
    # ============================================================
    print("\n[2/5] Running experiments...")
    
    experiments = [
        {"n_estimators": 50, "max_depth": 5, "run_name": "rf-small"},
        {"n_estimators": 100, "max_depth": 10, "run_name": "rf-medium"},
        {"n_estimators": 200, "max_depth": 15, "run_name": "rf-large"},
    ]
    
    results = []
    for exp in experiments:
        r2 = run_experiment(
            X_train, X_test, y_train, y_test, feature_names,
            **exp
        )
        results.append({"name": exp["run_name"], "r2": r2})
    
    # ============================================================
    # 결과 요약
    # ============================================================
    print("\n" + "=" * 60)
    print("  Experiment Results Summary")
    print("=" * 60)
    print(f"\n  {'Run Name':<15} {'R2 Score':<10}")
    print("  " + "-" * 25)
    
    best = max(results, key=lambda x: x["r2"])
    for r in results:
        marker = " ← Best" if r["name"] == best["name"] else ""
        print(f"  {r['name']:<15} {r['r2']:.4f}{marker}")
    
    print("\n" + "=" * 60)
    print("  ✅ All experiments completed!")
    print("=" * 60)
    print(f"\n💡 View results at MLflow UI: http://localhost:5000")
    print(f"   Experiment: {experiment_name}")


if __name__ == '__main__':
    main()
