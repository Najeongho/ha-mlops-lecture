"""
Lab 3-2: E2E Pipeline Components
================================

이 패키지는 E2E ML Pipeline의 개별 컴포넌트들을 포함합니다.

Components:
    - data_loader: 데이터 로드
    - preprocessor: 데이터 전처리
    - trainer: 모델 학습
    - evaluator: 모델 평가
    - deployer: 모델 배포
"""

from .data_loader import load_data
from .preprocessor import preprocess
from .trainer import train_model
from .evaluator import evaluate_model
from .deployer import deploy_model

__all__ = [
    'load_data',
    'preprocess', 
    'train_model',
    'evaluate_model',
    'deploy_model'
]
