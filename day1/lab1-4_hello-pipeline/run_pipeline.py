"""
Lab 1-4: Pipeline 실행 스크립트
==============================

컴파일된 파이프라인을 Kubeflow에 제출하는 스크립트

사용법:
    python run_pipeline.py [--a 10] [--b 20] [--factor 3]
"""

import argparse
import kfp
from hello_pipeline import hello_pipeline


def main():
    """파이프라인을 실행합니다."""
    
    # 인자 파서 설정
    parser = argparse.ArgumentParser(description='Hello World Pipeline 실행')
    parser.add_argument('--a', type=int, default=10, help='첫 번째 숫자 (기본값: 10)')
    parser.add_argument('--b', type=int, default=20, help='두 번째 숫자 (기본값: 20)')
    parser.add_argument('--factor', type=int, default=3, help='곱할 값 (기본값: 3)')
    parser.add_argument('--experiment', type=str, default='hello-experiment', 
                        help='실험 이름 (기본값: hello-experiment)')
    parser.add_argument('--run-name', type=str, default=None, 
                        help='Run 이름 (기본값: 자동 생성)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Lab 1-4: Hello World Pipeline 실행")
    print("=" * 60)
    print(f"\n  Parameters:")
    print(f"    - a: {args.a}")
    print(f"    - b: {args.b}")
    print(f"    - factor: {args.factor}")
    print(f"    - Experiment: {args.experiment}")
    print(f"\n  Expected Result: ({args.a} + {args.b}) * {args.factor} = {(args.a + args.b) * args.factor}")
    
    # KFP 클라이언트 생성
    try:
        print("\n[1/2] Connecting to Kubeflow Pipelines...")
        client = kfp.Client()
        
        print(f"  ✅ Connected!")
        print(f"  Host: {client._host}")
        print(f"  Namespace: {client.get_user_namespace()}")
        
    except Exception as e:
        print(f"\n  ❌ Failed to connect to Kubeflow: {e}")
        print("\n  💡 Make sure you're running inside Kubeflow Jupyter")
        print("     or that port-forwarding is set up correctly.")
        return
    
    # 파이프라인 실행
    try:
        print("\n[2/2] Submitting Pipeline...")
        
        run = client.create_run_from_pipeline_func(
            hello_pipeline,
            arguments={
                'a': args.a,
                'b': args.b,
                'factor': args.factor
            },
            experiment_name=args.experiment,
            run_name=args.run_name
        )
        
        print(f"\n  ✅ Pipeline submitted successfully!")
        print(f"\n  Run Details:")
        print(f"    - Run ID: {run.run_id}")
        print(f"    - Experiment: {args.experiment}")
        
        print("\n" + "=" * 60)
        print("  💡 Check Kubeflow Dashboard → Runs to see the results")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n  ❌ Failed to submit pipeline: {e}")


if __name__ == '__main__':
    main()
