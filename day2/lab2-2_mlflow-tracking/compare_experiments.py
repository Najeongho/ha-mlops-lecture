"""
Lab 2-2: MLflow 실험 비교 스크립트
==================================

여러 실험의 결과를 비교하고 시각화합니다.

사용법:
    python compare_experiments.py [--experiment california-housing-lab]
"""

import argparse
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import matplotlib.pyplot as plt
import os


def configure_mlflow():
    """MLflow 환경 설정"""
    tracking_uri = os.getenv(
        'MLFLOW_TRACKING_URI',
        'http://mlflow-server-service.mlflow-system.svc.cluster.local:5000'
    )
    mlflow.set_tracking_uri(tracking_uri)
    return tracking_uri


def get_experiment_runs(experiment_name: str) -> pd.DataFrame:
    """실험의 모든 Run을 가져옵니다."""
    client = MlflowClient()
    
    # 실험 ID 가져오기
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        print(f"❌ 실험 '{experiment_name}'을 찾을 수 없습니다.")
        return pd.DataFrame()
    
    # 모든 Run 검색
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.r2 DESC"]
    )
    
    return runs


def compare_metrics(runs_df: pd.DataFrame):
    """메트릭 비교"""
    print("\n" + "=" * 70)
    print("  📊 실험 결과 비교")
    print("=" * 70)
    
    # 필요한 컬럼 선택
    metric_cols = ['metrics.r2', 'metrics.rmse', 'metrics.mae', 'metrics.mse']
    param_cols = [col for col in runs_df.columns if col.startswith('params.')]
    
    display_cols = ['tags.mlflow.runName'] + metric_cols
    available_cols = [col for col in display_cols if col in runs_df.columns]
    
    if not available_cols:
        print("  ⚠️  메트릭 데이터가 없습니다.")
        return
    
    # 데이터 정리
    comparison_df = runs_df[available_cols].copy()
    comparison_df.columns = [col.split('.')[-1] for col in comparison_df.columns]
    
    # 정렬 및 출력
    if 'r2' in comparison_df.columns:
        comparison_df = comparison_df.sort_values('r2', ascending=False)
    
    print("\n  Run Name          R2        RMSE      MAE       MSE")
    print("  " + "-" * 60)
    
    for _, row in comparison_df.iterrows():
        run_name = row.get('runName', 'N/A')[:18].ljust(18)
        r2 = f"{row.get('r2', 0):.4f}".ljust(10) if pd.notna(row.get('r2')) else 'N/A'.ljust(10)
        rmse = f"{row.get('rmse', 0):.4f}".ljust(10) if pd.notna(row.get('rmse')) else 'N/A'.ljust(10)
        mae = f"{row.get('mae', 0):.4f}".ljust(10) if pd.notna(row.get('mae')) else 'N/A'.ljust(10)
        mse = f"{row.get('mse', 0):.4f}" if pd.notna(row.get('mse')) else 'N/A'
        
        print(f"  {run_name}{r2}{rmse}{mae}{mse}")
    
    # 최고 성능 모델
    if 'r2' in comparison_df.columns and len(comparison_df) > 0:
        best_idx = comparison_df['r2'].idxmax()
        best_run = comparison_df.loc[best_idx]
        print("\n  " + "-" * 60)
        print(f"  🏆 최고 성능: {best_run.get('runName', 'N/A')} (R2: {best_run.get('r2', 0):.4f})")
    
    return comparison_df


def plot_comparison(runs_df: pd.DataFrame, output_path: str = "comparison.png"):
    """비교 그래프 생성"""
    
    # 데이터 준비
    metric_data = []
    for _, row in runs_df.iterrows():
        run_name = row.get('tags.mlflow.runName', 'Unknown')
        r2 = row.get('metrics.r2', None)
        rmse = row.get('metrics.rmse', None)
        
        if pd.notna(r2) and pd.notna(rmse):
            metric_data.append({
                'name': run_name,
                'r2': r2,
                'rmse': rmse
            })
    
    if not metric_data:
        print("  ⚠️  시각화할 데이터가 없습니다.")
        return
    
    df = pd.DataFrame(metric_data).sort_values('r2', ascending=True)
    
    # 그래프 생성
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df)))
    
    # R2 Score
    axes[0].barh(df['name'], df['r2'], color=colors)
    axes[0].set_xlabel('R2 Score', fontsize=12)
    axes[0].set_title('R2 Score Comparison', fontsize=14)
    axes[0].axvline(x=df['r2'].max(), color='red', linestyle='--', alpha=0.7, label='Best')
    axes[0].legend()
    
    # RMSE
    axes[1].barh(df['name'], df['rmse'], color=colors)
    axes[1].set_xlabel('RMSE', fontsize=12)
    axes[1].set_title('RMSE Comparison', fontsize=14)
    axes[1].axvline(x=df['rmse'].min(), color='red', linestyle='--', alpha=0.7, label='Best')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n  📈 비교 그래프 저장: {output_path}")


def list_experiments():
    """모든 실험 목록 출력"""
    client = MlflowClient()
    experiments = client.search_experiments()
    
    print("\n" + "=" * 60)
    print("  📁 등록된 실험 목록")
    print("=" * 60)
    
    for exp in experiments:
        run_count = len(mlflow.search_runs(experiment_ids=[exp.experiment_id]))
        print(f"  - {exp.name} ({run_count} runs)")
    
    print("=" * 60)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='MLflow 실험 비교')
    parser.add_argument('--experiment', type=str, default='california-housing-lab',
                        help='비교할 실험 이름')
    parser.add_argument('--list', action='store_true',
                        help='등록된 실험 목록 출력')
    parser.add_argument('--output', type=str, default='comparison.png',
                        help='비교 그래프 출력 파일')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Lab 2-2: MLflow 실험 비교")
    print("=" * 60)
    
    # MLflow 설정
    tracking_uri = configure_mlflow()
    print(f"\n  MLflow Tracking URI: {tracking_uri}")
    
    # 실험 목록 출력
    if args.list:
        list_experiments()
        return
    
    # 실험 Run 가져오기
    print(f"\n  실험: {args.experiment}")
    runs_df = get_experiment_runs(args.experiment)
    
    if runs_df.empty:
        print("  ⚠️  실험에 Run이 없습니다.")
        return
    
    print(f"  총 {len(runs_df)}개의 Run 발견")
    
    # 메트릭 비교
    compare_metrics(runs_df)
    
    # 시각화
    try:
        import numpy as np
        plot_comparison(runs_df, args.output)
    except ImportError:
        print("\n  ⚠️  matplotlib가 필요합니다: pip install matplotlib")
    
    print("\n" + "=" * 60)
    print("  ✅ 비교 완료!")
    print("=" * 60)


if __name__ == '__main__':
    import numpy as np  # plot_comparison에서 사용
    main()
