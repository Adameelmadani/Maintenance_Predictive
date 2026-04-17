"""
Standalone Script to Train All Models and Generate Benchmarks

Runs the full pipeline:
1. Load and preprocess data
2. Train all 5 regression models
3. Train all 2 classification models
4. Generate benchmark report
5. Save all models to disk
"""

from src.data_loader import DataLoader
from src.models.regression import RULModelSuite
from src.models.classification import DiagnosticModelSuite
from src.models.model_utils import ModelUtils
import json
import pandas as pd


def main():
    print("\n" + "="*80)
    print(" " * 15 + "🚀 PREDICTIVE MAINTENANCE — MODEL TRAINING PIPELINE")
    print("="*80)
    
    # ========== STEP 1: Load Data ==========
    print("\n📊 STEP 1: Data Loading & Preprocessing")
    print("-" * 80)
    
    loader = DataLoader(data_dir='data', processed_dir='data/processed')
    data = loader.get_processed_data(
        train_file='data/raw/CMaps/train_FD001.txt',
        test_file='data/raw/CMaps/test_FD001.txt',
        rul_file='data/raw/CMaps/RUL_FD001.txt'
    )
    
    X_train = data['X_train']
    y_rul_train = data['y_rul_train']
    y_cls_train = data['y_cls_train']
    X_test = data['X_test']
    y_rul_test = data['y_rul_test']
    
    # ========== STEP 2: Train RUL Models ==========
    print("\n\n📈 STEP 2: Training RUL Prediction Models (5 models)")
    print("-" * 80)
    
    rul_suite = RULModelSuite(model_dir='models')
    rul_suite.train_all_models(X_train, y_rul_train, X_test, y_rul_test)
    
    print("\n📊 RUL Model Benchmarks:")
    print("-" * 80)
    rul_benchmarks = rul_suite.get_benchmark_table()
    df_rul = pd.DataFrame(rul_benchmarks).T
    print(df_rul.to_string())
    
    # ========== STEP 3: Train Classification Models ==========
    print("\n\n🎯 STEP 3: Training Diagnostic Classification Models (2 models)")
    print("-" * 80)
    
    cls_suite = DiagnosticModelSuite(model_dir='models')
    # Compute test health labels based on test RUL
    y_cls_test = (y_rul_test <= 30).astype(int)
    cls_suite.train_all_models(X_train, y_cls_train, X_test, y_cls_test)
    
    print("\n📊 Diagnostic Model Benchmarks:")
    print("-" * 80)
    cls_benchmarks = cls_suite.get_benchmark_table()
    df_cls = pd.DataFrame(cls_benchmarks).T
    print(df_cls.to_string())
    
    # ========== STEP 4: Save Comprehensive Benchmark Report ==========
    print("\n\n✨ STEP 4: Generating Comprehensive Benchmark Report")
    print("-" * 80)
    
    # Create full report
    full_report = {
        'RUL_Models': {
            'benchmarks': rul_benchmarks,
            'best_mae': min(rul_suite.results, key=lambda x: rul_suite.results[x]['mae']),
            'best_rmse': min(rul_suite.results, key=lambda x: rul_suite.results[x]['rmse']),
            'best_r2': max(rul_suite.results, key=lambda x: rul_suite.results[x]['r2']),
            'detailed_results': rul_suite.results
        },
        'Classification_Models': {
            'benchmarks': cls_benchmarks,
            'confusion_matrices': cls_suite.get_confusion_matrices(),
            'detailed_results': cls_suite.results
        },
        'Data_Summary': {
            'train_samples': int(X_train.shape[0]),
            'test_samples': int(X_test.shape[0]),
            'n_features': int(X_train.shape[1]),
            'features': data['feature_cols']
        }
    }
    
    # Save to JSON
    ModelUtils.save_results_json(full_report, 'models/benchmark_results.json')
    
    # ========== STEP 5: Summary ==========
    print("\n\n" + "="*80)
    print(" " * 20 + "✅ ALL MODELS TRAINED AND SAVED SUCCESSFULLY!")
    print("="*80)
    
    print("\n📁 Saved Artifacts:")
    print("  ✓ RUL Models:")
    print("    - models/rul_huber.pkl")
    print("    - models/rul_decisiontree.pkl")
    print("    - models/rul_mlp.pkl")
    print("    - models/rul_randomforest.pkl")
    print("    - models/rul_xgboost.pkl")
    print("  ✓ Classification Models:")
    print("    - models/cls_randomforest.pkl")
    print("    - models/cls_svm.pkl")
    print("  ✓ Benchmark Report:")
    print("    - models/benchmark_results.json")
    print("  ✓ Processed Data:")
    print("    - data/processed/X_train.npy")
    print("    - data/processed/X_test.npy")
    print("    - data/processed/y_rul_train.npy")
    print("    - data/processed/y_rul_test.npy")
    print("    - data/processed/y_cls_train.npy")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
