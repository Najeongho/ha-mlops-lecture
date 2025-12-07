"""
Lab 1-4: Hello World Pipeline
==============================

A simple pipeline that performs addition and multiplication operations.

Pipeline Structure:
    add(a, b) -> multiply(sum, factor) -> print_result(product)

Usage:
    python hello_pipeline.py
"""

import warnings
warnings.filterwarnings('ignore')

import kfp
from kfp import dsl
from kfp import compiler


# ============================================================
# Component 1: add - Add two numbers
# ============================================================

@dsl.component(base_image='python:3.11')
def add(a: int, b: int) -> int:
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    result = a + b
    print(f"Add: {a} + {b} = {result}")
    return result


# ============================================================
# Component 2: multiply - Multiply by a factor
# ============================================================

@dsl.component(base_image='python:3.11')
def multiply(x: int, factor: int = 2) -> int:
    """
    Multiply a number by a factor.
    
    Args:
        x: Input number
        factor: Multiplier (default: 2)
    
    Returns:
        Product of x and factor
    """
    result = x * factor
    print(f"Multiply: {x} * {factor} = {result}")
    return result


# ============================================================
# Component 3: print_result - Print final result
# ============================================================

@dsl.component(base_image='python:3.11')
def print_result(value: int):
    """
    Print the final result.
    
    Args:
        value: Value to print
    """
    print("=" * 50)
    print(f"Final Result: {value}")
    print("=" * 50)


# ============================================================
# Pipeline Definition
# ============================================================

@dsl.pipeline(
    name='Hello World Pipeline',
    description='Simple addition and multiplication pipeline'
)
def hello_pipeline(
    a: int = 3,
    b: int = 5,
    factor: int = 2
):
    """
    Hello World Pipeline
    
    Args:
        a: First number (default: 3)
        b: Second number (default: 5)
        factor: Multiplier (default: 2)
    
    Calculation:
        1. add: a + b
        2. multiply: (a + b) * factor
        3. print_result: Output result
    """
    
    # Step 1: Calculate a + b
    add_task = add(a=a, b=b)
    
    # Step 2: Calculate (a + b) * factor
    multiply_task = multiply(
        x=add_task.output,
        factor=factor
    )
    
    # Step 3: Print result
    print_result(value=multiply_task.output)


# ============================================================
# Main - Compile Pipeline
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  Lab 1-4: Hello World Pipeline")
    print("=" * 60)
    print(f"\nKFP Version: {kfp.__version__}")
    
    # Compile pipeline
    print("\n" + "=" * 60)
    print("  Compiling Pipeline...")
    print("=" * 60)
    
    pipeline_file = 'hello_pipeline_en.yaml'
    compiler.Compiler().compile(
        pipeline_func=hello_pipeline,
        package_path=pipeline_file
    )
    
    print(f"\nSuccess! File: {pipeline_file}")
    
    print("\n" + "=" * 60)
    print("  Next Steps")
    print("=" * 60)
    print("\n1. Download 'hello_pipeline_en.yaml'")
    print("2. Kubeflow Dashboard -> Pipelines -> Upload pipeline")
    print("3. Upload the YAML file")
    print("4. Create run with parameters:")
    print("   - a: 10")
    print("   - b: 20")
    print("   - factor: 3")
    print("5. Expected result: (10 + 20) * 3 = 90")
    print("\n" + "=" * 60)
