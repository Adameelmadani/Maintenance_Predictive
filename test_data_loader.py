"""
Test script for data_loader.py
Verifies the full preprocessing pipeline on FD001 dataset
"""

from src.data_loader import DataLoader
import os

if __name__ == "__main__":
    # Initialize loader
    loader = DataLoader(data_dir='data', processed_dir='data/processed')
    
    # Updated paths to account for CMaps subdirectory
    train_file = 'data/raw/CMaps/train_FD001.txt'
    test_file = 'data/raw/CMaps/test_FD001.txt'
    rul_file = 'data/raw/CMaps/RUL_FD001.txt'
    
    print("\n🚀 Testing Data Pipeline on FD001...\n")
    
    # Run full pipeline
    data = loader.get_processed_data(
        train_file=train_file,
        test_file=test_file,
        rul_file=rul_file
    )
    
    print("\n✅ Data Pipeline Test PASSED!")
    print(f"\nShape Summary:")
    print(f"  X_train: {data['X_train'].shape}")
    print(f"  y_rul_train: {data['y_rul_train'].shape}")
    print(f"  y_cls_train: {data['y_cls_train'].shape}")
    print(f"  X_test: {data['X_test'].shape}")
    print(f"  y_rul_test: {data['y_rul_test'].shape}")
    print(f"\nFeatures ({len(data['feature_cols'])}): {data['feature_cols']}")
