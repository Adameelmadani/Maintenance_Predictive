"""
Data Loading and Preprocessing Pipeline for NASA C-MAPSS Turbofan Engine Dataset

This module handles:
1. Loading raw NASA C-MAPSS data
2. Computing Remaining Useful Life (RUL)
3. Feature normalization
4. Binary health label generation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path


class DataLoader:
    """
    Load and preprocess NASA C-MAPSS turbofan engine degradation dataset.
    
    Handles the full pipeline: raw loading → RUL computation → normalization → train/test split
    """
    
    # Column names for the dataset (26 total: id, cycle, 3 op_settings, 21 sensors)
    COLUMNS = [
        'engine_id', 'cycle', 
        'op_setting_1', 'op_setting_2', 'op_setting_3',
        'sensor_1', 'sensor_2', 'sensor_3', 'sensor_4', 'sensor_5',
        'sensor_6', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_10',
        'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15',
        'sensor_16', 'sensor_17', 'sensor_18', 'sensor_19', 'sensor_20',
        'sensor_21'
    ]
    
    # Sensors to drop (constant or near-zero-variance)
    DROP_SENSORS = ['sensor_1', 'sensor_5', 'sensor_6', 'sensor_10', 'sensor_16', 'sensor_18', 'sensor_19']
    
    def __init__(self, data_dir='data', processed_dir='data/processed'):
        """
        Initialize DataLoader.
        
        Args:
            data_dir (str): Path to raw data directory
            processed_dir (str): Path to save processed data
        """
        self.data_dir = Path(data_dir)
        self.processed_dir = Path(processed_dir)
        self.scaler = StandardScaler()
        
        # Ensure processed directory exists
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw(self, filepath, set_type='train'):
        """
        Load raw NASA C-MAPSS txt file and add column names.
        
        Args:
            filepath (str): Path to raw .txt file
            set_type (str): 'train' or 'test' (for reference)
            
        Returns:
            pd.DataFrame: DataFrame with proper column names
        """
        df = pd.read_csv(filepath, sep='\s+', header=None, names=self.COLUMNS)
        print(f"✓ Loaded {set_type} set: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    
    def compute_rul(self, df):
        """
        Compute Remaining Useful Life (RUL) for training data.
        
        RUL = max_cycle_per_engine - current_cycle
        
        Args:
            df (pd.DataFrame): Training dataframe with engine_id and cycle columns
            
        Returns:
            pd.DataFrame: DataFrame with added 'RUL' column
        """
        df = df.copy()
        max_cycles = df.groupby('engine_id')['cycle'].max().reset_index()
        max_cycles.columns = ['engine_id', 'max_cycle']
        df = df.merge(max_cycles, on='engine_id', how='left')
        df['RUL'] = df['max_cycle'] - df['cycle']
        df = df.drop('max_cycle', axis=1)
        print(f"✓ Computed RUL: mean={df['RUL'].mean():.1f}, min={df['RUL'].min()}, max={df['RUL'].max()}")
        return df
    
    def clip_rul(self, df, clip=125):
        """
        Apply piecewise linear RUL clipping at threshold (standard CMAPSS practice).
        
        Values above clip threshold are set to clip value.
        
        Args:
            df (pd.DataFrame): DataFrame with 'RUL' column
            clip (int): Clipping threshold in cycles
            
        Returns:
            pd.DataFrame: DataFrame with clipped RUL
        """
        df = df.copy()
        df['RUL'] = df['RUL'].apply(lambda x: min(x, clip))
        print(f"✓ Applied RUL clipping at {clip} cycles: mean={df['RUL'].mean():.1f}")
        return df
    
    def label_health(self, df, threshold=30):
        """
        Create binary health label column.
        
        0 = Healthy (RUL > threshold)
        1 = Degraded/Faulty (RUL ≤ threshold)
        
        Args:
            df (pd.DataFrame): DataFrame with 'RUL' column
            threshold (int): RUL threshold for health labeling
            
        Returns:
            pd.DataFrame: DataFrame with 'health_label' column
        """
        df = df.copy()
        df['health_label'] = (df['RUL'] <= threshold).astype(int)
        print(f"✓ Created health labels: {(df['health_label']==0).sum()} healthy, {(df['health_label']==1).sum()} degraded")
        return df
    
    def normalize(self, df_train, df_test, exclude_cols=None):
        """
        Fit StandardScaler on training data and normalize both train & test.
        
        Args:
            df_train (pd.DataFrame): Training data
            df_test (pd.DataFrame): Test data
            exclude_cols (list): Columns to exclude from normalization (e.g., ids, labels)
            
        Returns:
            tuple: (df_train_norm, df_test_norm)
        """
        if exclude_cols is None:
            exclude_cols = ['engine_id', 'cycle', 'RUL', 'health_label']
        
        # Identify numeric columns to normalize
        numeric_cols = [col for col in df_train.columns 
                       if col not in exclude_cols and df_train[col].dtype in ['float64', 'int64']]
        
        # Fit scaler on training data
        self.scaler.fit(df_train[numeric_cols])
        
        # Transform both train and test
        df_train_norm = df_train.copy()
        df_test_norm = df_test.copy()
        
        df_train_norm[numeric_cols] = self.scaler.transform(df_train[numeric_cols])
        df_test_norm[numeric_cols] = self.scaler.transform(df_test[numeric_cols])
        
        print(f"✓ Normalized {len(numeric_cols)} numeric columns using StandardScaler")
        return df_train_norm, df_test_norm
    
    def drop_constant_sensors(self, df):
        """
        Drop low-variance sensors as specified in preprocessing rules.
        
        Args:
            df (pd.DataFrame): DataFrame with sensor columns
            
        Returns:
            pd.DataFrame: DataFrame with constant sensors removed
        """
        df = df.copy()
        cols_to_drop = [col for col in self.DROP_SENSORS if col in df.columns]
        df = df.drop(columns=cols_to_drop)
        print(f"✓ Dropped {len(cols_to_drop)} constant/low-variance sensors: {cols_to_drop}")
        return df
    
    def get_processed_data(self, train_file=None, test_file=None, rul_file=None):
        """
        Full pipeline: load → preprocess → normalize → return train/test splits.
        
        Automatically detects FD001 files if paths not provided.
        
        Args:
            train_file (str): Path to training file (auto-detects if None)
            test_file (str): Path to test file (auto-detects if None)
            rul_file (str): Path to RUL labels file (auto-detects if None)
            
        Returns:
            dict: {
                'X_train': feature array (train),
                'y_rul_train': RUL targets (train),
                'y_cls_train': health labels (train),
                'X_test': feature array (test),
                'y_rul_test': RUL targets (test),
                'df_train': full preprocessed training dataframe,
                'df_test': full preprocessed test dataframe,
                'scaler': fitted StandardScaler
            }
        """
        # Auto-detect FD001 files
        if train_file is None:
            train_file = self.data_dir / 'raw' / 'train_FD001.txt'
        if test_file is None:
            test_file = self.data_dir / 'raw' / 'test_FD001.txt'
        if rul_file is None:
            rul_file = self.data_dir / 'raw' / 'RUL_FD001.txt'
        
        print("\n📊 Starting Data Pipeline...")
        print("=" * 60)
        
        # 1. Load raw data
        df_train = self.load_raw(train_file, 'train')
        df_test = self.load_raw(test_file, 'test')
        
        # 2. Compute RUL for training set
        df_train = self.compute_rul(df_train)
        
        # 3. Clip RUL at 125
        df_train = self.clip_rul(df_train, clip=125)
        
        # 4. Load RUL labels for test set (one per engine)
        rul_values = pd.read_csv(rul_file, header=None, names=['RUL'])['RUL'].values
        # Create mapping: engine_id -> RUL value
        engine_ids_test = df_test['engine_id'].unique()
        rul_mapping = {engine_id: rul_values[engine_id - 1] for engine_id in engine_ids_test}
        df_test['RUL'] = df_test['engine_id'].map(rul_mapping)
        print(f"✓ Loaded test set RUL: mean={df_test['RUL'].mean():.1f}, min={df_test['RUL'].min()}, max={df_test['RUL'].max()}")
        
        # 5. Create health labels
        df_train = self.label_health(df_train, threshold=30)
        df_test = self.label_health(df_test, threshold=30)
        
        # 6. Drop constant sensors
        df_train = self.drop_constant_sensors(df_train)
        df_test = self.drop_constant_sensors(df_test)
        
        # 7. Normalize
        df_train, df_test = self.normalize(df_train, df_test)
        
        # 8. Separate features and targets
        exclude = ['engine_id', 'cycle', 'RUL', 'health_label']
        feature_cols = [col for col in df_train.columns if col not in exclude]
        
        X_train = df_train[feature_cols].values
        y_rul_train = df_train['RUL'].values
        y_cls_train = df_train['health_label'].values
        
        X_test = df_test[feature_cols].values
        y_rul_test = df_test['RUL'].values
        
        print(f"\n✓ Feature matrix: {len(feature_cols)} features")
        print(f"  Train: X={X_train.shape}, y_rul={y_rul_train.shape}, y_cls={y_cls_train.shape}")
        print(f"  Test:  X={X_test.shape}, y_rul={y_rul_test.shape}")
        print("=" * 60)
        
        # Save processed datasets
        np.save(self.processed_dir / 'X_train.npy', X_train)
        np.save(self.processed_dir / 'X_test.npy', X_test)
        np.save(self.processed_dir / 'y_rul_train.npy', y_rul_train)
        np.save(self.processed_dir / 'y_rul_test.npy', y_rul_test)
        np.save(self.processed_dir / 'y_cls_train.npy', y_cls_train)
        df_train.to_csv(self.processed_dir / 'train_processed.csv', index=False)
        df_test.to_csv(self.processed_dir / 'test_processed.csv', index=False)
        print(f"\n💾 Saved processed data to {self.processed_dir}/")
        
        return {
            'X_train': X_train,
            'y_rul_train': y_rul_train,
            'y_cls_train': y_cls_train,
            'X_test': X_test,
            'y_rul_test': y_rul_test,
            'df_train': df_train,
            'df_test': df_test,
            'scaler': self.scaler,
            'feature_cols': feature_cols
        }
