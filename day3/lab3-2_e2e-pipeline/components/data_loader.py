"""
Lab 3-2: 데이터 로드 컴포넌트
============================

데이터셋을 로드하고 저장하는 컴포넌트
"""

from kfp.components import create_component_from_func


@create_component_from_func
def load_data(
    data_source: str = "sklearn",
    output_path: str = "/tmp/data.csv"
) -> str:
    """
    데이터를 로드하고 CSV로 저장합니다.
    
    Args:
        data_source: 데이터 소스 ("sklearn" 또는 S3 경로)
        output_path: 출력 파일 경로
    
    Returns:
        저장된 데이터 파일 경로
    """
    import pandas as pd
    from sklearn.datasets import fetch_california_housing
    
    print("=" * 50)
    print("  Component: Load Data")
    print("=" * 50)
    
    # 데이터 로드
    if data_source == "sklearn":
        print("\n  데이터 소스: sklearn (California Housing)")
        data = fetch_california_housing()
        df = pd.DataFrame(data.data, columns=data.feature_names)
        df['target'] = data.target
    else:
        print(f"\n  데이터 소스: {data_source}")
        df = pd.read_csv(data_source)
    
    # 데이터 정보 출력
    print(f"\n  📊 데이터 정보:")
    print(f"     - 행 수: {len(df)}")
    print(f"     - 열 수: {len(df.columns)}")
    print(f"     - 피처: {list(df.columns[:-1])}")
    print(f"     - 타겟: {df.columns[-1]}")
    
    # 저장
    df.to_csv(output_path, index=False)
    print(f"\n  ✅ 데이터 저장: {output_path}")
    
    return output_path


# 컴포넌트 직접 실행 시
if __name__ == "__main__":
    # 테스트
    result = load_data.python_func(
        data_source="sklearn",
        output_path="/tmp/test_data.csv"
    )
    print(f"\n결과: {result}")
