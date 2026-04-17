"""
Classification Models for Engine Health Diagnostics

Implements 2 diagnostic models:
1. Random Forest Classifier (health status classification)
2. SVM Classifier (support vector machine)

Each model identifies if an engine is in healthy or degraded state (binary classification).
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
from pathlib import Path


class DiagnosticModelSuite:
    """
    Suite of 2 diagnostic (classification) models for engine health status.
    """
    
    def __init__(self, model_dir='models'):
        """
        Initialize diagnostic model suite.
        
        Args:
            model_dir (str): Directory to save trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}
        self.results = {}
    
    def build_random_forest(self):
        """Build Random Forest Classifier."""
        return RandomForestClassifier(
            n_estimators=200,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
    
    def build_svm(self):
        """Build SVM Classifier."""
        return SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42
        )
    
    def train_model(self, model_name, X_train, y_train, X_test, y_test):
        """
        Train a single diagnostic model and evaluate on test set.
        
        Args:
            model_name (str): Name of model ('RandomForest' or 'SVM')
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training labels (0=healthy, 1=degraded)
            X_test (np.ndarray): Test features
            y_test (np.ndarray): Test labels
            
        Returns:
            dict: {
                'model': trained model,
                'accuracy': accuracy score,
                'precision': precision score,
                'recall': recall score,
                'f1': F1 score,
                'confusion_matrix': confusion matrix,
                'y_pred': predicted labels,
                'y_proba': prediction probabilities (if available)
            }
        """
        print(f"\n  Training {model_name}...", end=" ", flush=True)
        
        # Select model builder
        builders = {
            'RandomForest': self.build_random_forest,
            'SVM': self.build_svm
        }
        
        model = builders[model_name]()
        
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Get probabilities if available
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = None
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        
        print(f"✓ Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
        
        return {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm,
            'y_pred': y_pred,
            'y_proba': y_proba,
            'y_test': y_test,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """
        Train all diagnostic models and store results.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training labels
            X_test (np.ndarray): Test features
            y_test (np.ndarray): Test labels
        """
        model_names = ['RandomForest', 'SVM']
        
        print("\n🎯 Training Diagnostic Classification Models")
        print("=" * 70)
        
        for model_name in model_names:
            result = self.train_model(model_name, X_train, y_train, X_test, y_test)
            self.models[model_name] = result['model']
            
            # Store results
            self.results[model_name] = {
                'accuracy': result['accuracy'],
                'precision': result['precision'],
                'recall': result['recall'],
                'f1': result['f1'],
                'confusion_matrix': result['confusion_matrix'].tolist(),
                'classification_report': result['classification_report'],
                'y_pred': result['y_pred'].tolist(),
                'y_test': result['y_test'].tolist()
            }
            
            if result['y_proba'] is not None:
                self.results[model_name]['y_proba'] = result['y_proba'].tolist()
            
            # Save model
            model_path = self.model_dir / f'cls_{model_name.lower()}.pkl'
            joblib.dump(result['model'], model_path)
        
        print("=" * 70)
    
    def get_benchmark_table(self):
        """
        Return benchmark results as formatted dictionary.
        
        Returns:
            dict: Benchmarks for all classifiers
        """
        benchmark = {}
        for model_name, metrics in self.results.items():
            benchmark[model_name] = {
                'Accuracy': round(metrics['accuracy'], 4),
                'Precision': round(metrics['precision'], 4),
                'Recall': round(metrics['recall'], 4),
                'F1': round(metrics['f1'], 4)
            }
        return benchmark
    
    def get_confusion_matrices(self):
        """
        Return confusion matrices for all models.
        
        Returns:
            dict: {model_name: [[TN, FP], [FN, TP]]}
        """
        matrices = {}
        for model_name, metrics in self.results.items():
            tn, fp, fn, tp = metrics['confusion_matrix'][0][0], metrics['confusion_matrix'][0][1], \
                             metrics['confusion_matrix'][1][0], metrics['confusion_matrix'][1][1]
            matrices[model_name] = {
                'TN': int(tn),
                'FP': int(fp),
                'FN': int(fn),
                'TP': int(tp)
            }
        return matrices
