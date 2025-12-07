"""
Lab 1-4: Hello World Pipeline
=============================

간단한 덧셈과 곱셈을 수행하는 첫 번째 Kubeflow Pipeline

파이프라인 구조:
    add(a, b) → multiply(sum, factor) → print_result(product)

사용법:
    python hello_pipeline.py
"""

from kfp.components import create_component_from_func
from kfp import dsl
from kfp import compiler


# ============================================================
# Component 1: add - 두 숫자를 더합니다
# ============================================================

@create_component_from_func
def add(a: int, b: int) -> int:
    """
    두 숫자를 더합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    
    Returns:
        a + b의 결과
    """
    result = a + b
    print(f"Add Component: {a} + {b} = {result}")
    return result


# ============================================================
# Component 2: multiply - 숫자에 factor를 곱합니다
# ============================================================

@create_component_from_func
def multiply(x: int, factor: int = 2) -> int:
    """
    숫자에 factor를 곱합니다.
    
    Args:
        x: 입력 숫자
        factor: 곱할 값 (기본값: 2)
    
    Returns:
        x * factor의 결과
    """
    result = x * factor
    print(f"Multiply Component: {x} * {factor} = {result}")
    return result


# ============================================================
# Component 3: print_result - 최종 결과를 출력합니다
# ============================================================

@create_component_from_func
def print_result(value: int):
    """
    최종 결과를 출력합니다.
    
    Args:
        value: 출력할 값
    """
    print("=" * 50)
    print(f"  🎉 Final Result: {value}")
    print("=" * 50)


# ============================================================
# Pipeline Definition
# ============================================================

@dsl.pipeline(
    name='Hello World Pipeline',
    description='간단한 덧셈과 곱셈을 수행하는 첫 번째 파이프라인'
)
def hello_pipeline(
    a: int = 3,
    b: int = 5,
    factor: int = 2
):
    """
    Hello World Pipeline
    
    Args:
        a: 첫 번째 숫자 (기본값: 3)
        b: 두 번째 숫자 (기본값: 5)
        factor: 곱할 값 (기본값: 2)
    
    계산 과정:
        1. add: a + b
        2. multiply: (a + b) * factor
        3. print_result: 결과 출력
    """
    
    # Step 1: a + b 계산
    add_task = add(a=a, b=b)
    
    # Step 2: (a + b) * factor 계산
    multiply_task = multiply(
        x=add_task.output,
        factor=factor
    )
    
    # Step 3: 결과 출력
    print_result(value=multiply_task.output)


# ============================================================
# Main - 컴파일 및 실행
# ============================================================

if __name__ == '__main__':
    import kfp
    
    # 파이프라인 컴파일
    print("=" * 60)
    print("  Compiling Pipeline...")
    print("=" * 60)
    
    pipeline_file = 'hello_pipeline.yaml'
    compiler.Compiler().compile(
        pipeline_func=hello_pipeline,
        package_path=pipeline_file
    )
    print(f"✅ Pipeline compiled: {pipeline_file}")
    
    # 파이프라인 실행 (Kubeflow 환경에서만)
    try:
        print("\n" + "=" * 60)
        print("  Submitting Pipeline...")
        print("=" * 60)
        
        client = kfp.Client()
        
        run = client.create_run_from_pipeline_func(
            hello_pipeline,
            arguments={
                'a': 10,
                'b': 20,
                'factor': 3
            },
            experiment_name='hello-experiment',
            run_name='hello-run'
        )
        
        print(f"✅ Pipeline submitted!")
        print(f"   Run ID: {run.run_id}")
        print(f"   Expected Result: (10 + 20) * 3 = 90")
        print("\n💡 Check the Kubeflow Dashboard → Runs to see the results")
        
    except Exception as e:
        print(f"⚠️  Could not submit pipeline: {e}")
        print("   Make sure you're running this inside Kubeflow Jupyter")
        print(f"\n✅ Pipeline YAML file created: {pipeline_file}")
        print("   You can upload this file manually via Kubeflow UI")
