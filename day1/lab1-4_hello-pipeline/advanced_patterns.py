"""
[실습 1-4 확장] 고급 파이프라인 패턴
- 슬라이드 84: 조건부 분기 (dsl.Condition)
- 슬라이드 85-86: 병렬 실행 (dsl.ParallelFor)

현대오토에버 MLOps 교육
"""

from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics
from typing import List


# ============================================================
# Part 1: 조건부 분기 (Conditional Branching)
# 슬라이드 84 - dsl.Condition 활용
# ============================================================

@component(
    base_image="python:3.9-slim",
    packages_to_install=["scikit-learn==1.3.2", "pandas==2.0.3"]
)
def train_model(
    algorithm: str,
    data_path: str,
    model: Output[Model],
    metrics: Output[Metrics]
) -> float:
    """모델 학습 및 정확도 반환"""
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    import joblib
    import json
    
    # 데이터 로드
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    
    # 알고리즘 선택
    if algorithm == "random_forest":
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        clf = LogisticRegression(max_iter=200, random_state=42)
    
    # 학습 및 평가
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    
    # 모델 저장
    joblib.dump(clf, model.path)
    
    # 메트릭 저장
    metrics.log_metric("accuracy", accuracy)
    metrics.log_metric("algorithm", algorithm)
    
    print(f"Algorithm: {algorithm}, Accuracy: {accuracy:.4f}")
    return accuracy


@component(base_image="python:3.9-slim")
def deploy_to_production(model_path: str, accuracy: float) -> str:
    """프로덕션 배포 (정확도가 임계값 이상일 때)"""
    print(f"✅ 모델을 프로덕션에 배포합니다!")
    print(f"   - 모델 경로: {model_path}")
    print(f"   - 정확도: {accuracy:.4f}")
    return f"Deployed with accuracy {accuracy:.4f}"


@component(base_image="python:3.9-slim")
def deploy_to_staging(model_path: str, accuracy: float) -> str:
    """스테이징 배포 (정확도가 임계값 미만일 때)"""
    print(f"⚠️ 모델을 스테이징에 배포합니다. (추가 검증 필요)")
    print(f"   - 모델 경로: {model_path}")
    print(f"   - 정확도: {accuracy:.4f}")
    return f"Staged for review with accuracy {accuracy:.4f}"


@component(base_image="python:3.9-slim")
def notify_failure(accuracy: float, threshold: float) -> str:
    """정확도 미달 알림"""
    print(f"❌ 모델 정확도가 기준 미달입니다.")
    print(f"   - 현재 정확도: {accuracy:.4f}")
    print(f"   - 요구 정확도: {threshold:.4f}")
    return f"Failed: {accuracy:.4f} < {threshold:.4f}"


@dsl.pipeline(
    name="conditional-deployment-pipeline",
    description="조건부 분기를 활용한 모델 배포 파이프라인"
)
def conditional_pipeline(
    algorithm: str = "random_forest",
    accuracy_threshold: float = 0.90,
    staging_threshold: float = 0.80
):
    """
    조건부 분기 파이프라인
    
    흐름도:
    ┌─────────────┐
    │ train_model │
    └──────┬──────┘
           │
           ▼
    ┌──────────────────┐
    │ accuracy >= 0.90 │──Yes──▶ deploy_to_production
    └────────┬─────────┘
             │ No
             ▼
    ┌──────────────────┐
    │ accuracy >= 0.80 │──Yes──▶ deploy_to_staging
    └────────┬─────────┘
             │ No
             ▼
       notify_failure
    """
    
    # Step 1: 모델 학습
    train_task = train_model(
        algorithm=algorithm,
        data_path="/data/iris"
    )
    
    # Step 2: 조건부 분기 - 프로덕션 배포
    with dsl.Condition(
        train_task.output >= accuracy_threshold,
        name="check-production-ready"
    ):
        deploy_to_production(
            model_path=train_task.outputs["model"],
            accuracy=train_task.output
        )
    
    # Step 3: 조건부 분기 - 스테이징 배포
    with dsl.Condition(
        (train_task.output < accuracy_threshold) & 
        (train_task.output >= staging_threshold),
        name="check-staging-ready"
    ):
        deploy_to_staging(
            model_path=train_task.outputs["model"],
            accuracy=train_task.output
        )
    
    # Step 4: 조건부 분기 - 실패 알림
    with dsl.Condition(
        train_task.output < staging_threshold,
        name="check-failed"
    ):
        notify_failure(
            accuracy=train_task.output,
            threshold=staging_threshold
        )


# ============================================================
# Part 2: 병렬 실행 (Parallel Execution)
# 슬라이드 85-86 - dsl.ParallelFor 활용
# ============================================================

@component(
    base_image="python:3.9-slim",
    packages_to_install=["scikit-learn==1.3.2"]
)
def train_with_hyperparams(
    n_estimators: int,
    max_depth: int,
    experiment_name: str
) -> dict:
    """하이퍼파라미터 조합으로 모델 학습"""
    from sklearn.datasets import load_iris
    from sklearn.model_selection import cross_val_score
    from sklearn.ensemble import RandomForestClassifier
    import json
    
    # 데이터 로드
    iris = load_iris()
    
    # 모델 학습 및 교차 검증
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    
    scores = cross_val_score(clf, iris.data, iris.target, cv=5)
    mean_score = scores.mean()
    std_score = scores.std()
    
    result = {
        "experiment": experiment_name,
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "mean_accuracy": float(mean_score),
        "std_accuracy": float(std_score)
    }
    
    print(f"[{experiment_name}] n_estimators={n_estimators}, "
          f"max_depth={max_depth}, accuracy={mean_score:.4f}±{std_score:.4f}")
    
    return result


@component(base_image="python:3.9-slim")
def aggregate_results(results: List[dict]) -> dict:
    """모든 실험 결과를 집계하고 최적 조합 선택"""
    import json
    
    print("=" * 60)
    print("하이퍼파라미터 탐색 결과")
    print("=" * 60)
    
    best_result = None
    best_accuracy = 0
    
    for result in results:
        print(f"  [{result['experiment']}] "
              f"n_estimators={result['n_estimators']}, "
              f"max_depth={result['max_depth']}, "
              f"accuracy={result['mean_accuracy']:.4f}")
        
        if result['mean_accuracy'] > best_accuracy:
            best_accuracy = result['mean_accuracy']
            best_result = result
    
    print("=" * 60)
    print(f"🏆 최적 조합: {best_result['experiment']}")
    print(f"   - n_estimators: {best_result['n_estimators']}")
    print(f"   - max_depth: {best_result['max_depth']}")
    print(f"   - accuracy: {best_result['mean_accuracy']:.4f}")
    print("=" * 60)
    
    return best_result


@dsl.pipeline(
    name="parallel-hyperparameter-search",
    description="병렬 실행을 활용한 하이퍼파라미터 탐색 파이프라인"
)
def parallel_pipeline():
    """
    병렬 실행 파이프라인
    
    흐름도:
                    ┌─────────────────────┐
                    │ Hyperparameter Grid │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ Exp 1       │     │ Exp 2       │     │ Exp 3       │
    │ n=50, d=3   │     │ n=100, d=5  │     │ n=200, d=10 │
    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  aggregate_results  │
                    └─────────────────────┘
    """
    
    # 하이퍼파라미터 그리드 정의
    hyperparameter_grid = [
        {"n_estimators": 50, "max_depth": 3, "name": "exp-1-small"},
        {"n_estimators": 100, "max_depth": 5, "name": "exp-2-medium"},
        {"n_estimators": 200, "max_depth": 10, "name": "exp-3-large"},
        {"n_estimators": 100, "max_depth": 3, "name": "exp-4-shallow"},
        {"n_estimators": 100, "max_depth": 15, "name": "exp-5-deep"},
        {"n_estimators": 150, "max_depth": 7, "name": "exp-6-balanced"},
    ]
    
    # 병렬로 모든 하이퍼파라미터 조합 실험
    with dsl.ParallelFor(
        items=hyperparameter_grid,
        parallelism=3  # 동시 실행 수 제한
    ) as hp:
        train_task = train_with_hyperparams(
            n_estimators=hp.n_estimators,
            max_depth=hp.max_depth,
            experiment_name=hp.name
        )
    
    # 모든 결과 집계
    aggregate_results(results=dsl.Collected(train_task.output))


# ============================================================
# Part 3: 조건부 분기 + 병렬 실행 결합
# ============================================================

@dsl.pipeline(
    name="advanced-ml-pipeline",
    description="조건부 분기와 병렬 실행을 결합한 고급 파이프라인"
)
def advanced_pipeline(
    run_hyperparameter_search: bool = True,
    accuracy_threshold: float = 0.95
):
    """
    고급 파이프라인 (조건부 분기 + 병렬 실행 결합)
    
    흐름도:
    ┌───────────────────────────┐
    │ run_hyperparameter_search │
    └─────────────┬─────────────┘
                  │
        ┌─────────┴─────────┐
        │ True              │ False
        ▼                   ▼
    ┌─────────┐       ┌─────────────┐
    │ParallelFor│      │ Single Train │
    │ HP Search│       │ (default)   │
    └────┬────┘       └──────┬──────┘
         │                   │
         └─────────┬─────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Conditional     │
         │ Deployment      │
         └─────────────────┘
    """
    
    # 하이퍼파라미터 탐색 여부에 따른 분기
    with dsl.Condition(run_hyperparameter_search == True, name="hp-search-enabled"):
        # 병렬 하이퍼파라미터 탐색
        hp_grid = [
            {"n_estimators": 100, "max_depth": 5, "name": "config-1"},
            {"n_estimators": 200, "max_depth": 10, "name": "config-2"},
            {"n_estimators": 150, "max_depth": 7, "name": "config-3"},
        ]
        
        with dsl.ParallelFor(items=hp_grid, parallelism=3) as hp:
            parallel_train = train_with_hyperparams(
                n_estimators=hp.n_estimators,
                max_depth=hp.max_depth,
                experiment_name=hp.name
            )
        
        best = aggregate_results(results=dsl.Collected(parallel_train.output))
    
    with dsl.Condition(run_hyperparameter_search == False, name="hp-search-disabled"):
        # 단일 학습 (기본 설정)
        single_train = train_model(
            algorithm="random_forest",
            data_path="/data/iris"
        )


# ============================================================
# 컴파일 및 실행
# ============================================================

if __name__ == "__main__":
    from kfp import compiler
    import os
    
    # 출력 디렉토리 생성
    os.makedirs("compiled", exist_ok=True)
    
    # 1. 조건부 분기 파이프라인 컴파일
    compiler.Compiler().compile(
        pipeline_func=conditional_pipeline,
        package_path="compiled/conditional_pipeline.yaml"
    )
    print("✅ 조건부 분기 파이프라인 컴파일 완료: compiled/conditional_pipeline.yaml")
    
    # 2. 병렬 실행 파이프라인 컴파일
    compiler.Compiler().compile(
        pipeline_func=parallel_pipeline,
        package_path="compiled/parallel_pipeline.yaml"
    )
    print("✅ 병렬 실행 파이프라인 컴파일 완료: compiled/parallel_pipeline.yaml")
    
    # 3. 고급 파이프라인 컴파일
    compiler.Compiler().compile(
        pipeline_func=advanced_pipeline,
        package_path="compiled/advanced_pipeline.yaml"
    )
    print("✅ 고급 파이프라인 컴파일 완료: compiled/advanced_pipeline.yaml")
    
    print("\n" + "=" * 60)
    print("모든 파이프라인 컴파일 완료!")
    print("Kubeflow UI에서 업로드하여 실행하세요.")
    print("=" * 60)
