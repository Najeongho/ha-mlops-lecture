"""
Lab 3-2: 데이터 전처리 컴포넌트
==============================

데이터 전처리 및 Train/Test 분할을 수행하는 컴포넌트
"""

from kfp.components import create_component_from_func


@create_component_from_func
def preprocess(
    data_path: str,
    test_size: float = 0.2,
    output_dir: str = "/tmp/processed"
) -> str:
    """
    데이터 전처리 및 Train/Test 분할
    
    Args:
        data_path: 입력 데이터 경로
        test_size: 테스트 세트 비율
        output_dir: 출력 디렉토리
    
    Returns:
        전처리된 데이터 디렉토리 경로
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import json
    import os
    
    print("=" * 50)
    print("  Component: Preprocess")
    print("=" * 50)
    
    # 데이터 로드
    print(f"\n  입력 파일: {data_path}")
    df = pd.read_csv(data_path)
    print(f"  로드된 행 수: {len(df)}")
    
    # 피처와 타겟 분리
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"\n  📊 데이터 분할:")
    print(f"     - 학습 샘플: {len(X_train)}")
    print(f"     - 테스트 샘플: {len(X_test)}")
    
    # 정규화
    print("\n  🔄 StandardScaler 적용 중...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 저장
    os.makedirs(output_dir, exist_ok=True)
    
    np.save(f"{output_dir}/X_train.npy", X_train_scaled)
    np.save(f"{output_dir}/X_test.npy", X_test_scaled)
    np.save(f"{output_dir}/y_train.npy", y_train.values)
    np.save(f"{output_dir}/y_test.npy", y_test.values)
    
    # 메타데이터 저장
    metadata = {
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_features": X_train.shape[1],
        "feature_names": list(X.columns),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist()
    }
    
    with open(f"{output_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n  ✅ 전처리 완료: {output_dir}")
    print(f"     - X_train.npy, X_test.npy")
    print(f"     - y_train.npy, y_test.npy")
    print(f"     - metadata.json")
    
    return output_dir


# 컴포넌트 직접 실행 시
if __name__ == "__main__":
    # 테스트
    result = preprocess.python_func(
        data_path="/tmp/test_data.csv",
        test_size=0.2,
        output_dir="/tmp/processed"
    )
    print(f"\n결과: {result}")
