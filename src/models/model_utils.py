"""
Model Utilities - Common functions for loading, saving, and evaluating models
"""

import joblib
import json
import numpy as np
from pathlib import Path


class ModelUtils:
    """Utilities for model I/O and management."""
    
    @staticmethod
    def save_model(model, filename):
        """
        Save trained model to disk using joblib.
        
        Args:
            model: Trained sklearn model
            filename (str): Path to save model
        """
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, filename)
        print(f"  ✓ Saved model to {filename}")
    
    @staticmethod
    def load_model(filename):
        """
        Load trained model from disk.
        
        Args:
            filename (str): Path to saved model
            
        Returns:
            Loaded model
        """
        return joblib.load(filename)
    
    @staticmethod
    def save_results_json(results_dict, filename):
        """
        Save results dictionary to JSON file.
        
        Args:
            results_dict (dict): Results to save
            filename (str): Output file path
        """
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        print(f"  ✓ Saved results to {filename}")
    
    @staticmethod
    def load_results_json(filename):
        """
        Load results from JSON file.
        
        Args:
            filename (str): Path to JSON file
            
        Returns:
            dict: Loaded results
        """
        with open(filename, 'r') as f:
            return json.load(f)