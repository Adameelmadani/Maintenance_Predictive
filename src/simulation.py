"""
Real-Time Data Stream Simulator for Turbofan Engine Monitoring

Simulates live engine sensor data by stepping through test set cycles,
enabling real-time visualization and alert triggering in Streamlit dashboard.
"""

import numpy as np
import pandas as pd


class DataStreamSimulator:
    """
    Mimics a real-time sensor stream by stepping through test set engine data.
    
    Maintains state for a single engine over multiple cycles, allowing incremental
    data retrieval for live streaming visualization.
    """
    
    def __init__(self, df_test, engine_id=1, speed_factor=1, model=None):
        """
        Initialize simulator for a specific engine's test data.
        
        Args:
            df_test (pd.DataFrame): Full test dataset
            engine_id (int): Engine ID to simulate (1-100)
            speed_factor (float): Simulation speed multiplier (1=real-time, 2=2x speed)
            model: Optional trained RUL model for predictions
        """
        self.df_test_full = df_test.copy()
        self.engine_id = engine_id
        self.speed_factor = speed_factor
        self.model = model
        
        # Filter data for selected engine
        self.df_engine = df_test[df_test['engine_id'] == engine_id].copy().reset_index(drop=True)
        
        if len(self.df_engine) == 0:
            raise ValueError(f"Engine {engine_id} not found in test set")
        
        # Simulation state
        self.current_cycle_idx = 0
        self.max_cycles = len(self.df_engine)
        self.history = []  # Stores all readings seen so far
        
        print(f"Simulator initialized for Engine {engine_id}: {self.max_cycles} cycles available")
    
    def reset(self):
        """
        Restart simulation from first cycle.
        """
        self.current_cycle_idx = 0
        self.history = []
        print(f"Simulator reset for Engine {self.engine_id}")
    
    def advance(self, steps=1):
        """
        Advance simulation by N cycles.
        
        Args:
            steps (int): Number of cycles to advance (default: 1)
            
        Returns:
            bool: True if advancing succeeded, False if simulation ended
        """
        new_idx = self.current_cycle_idx + steps
        
        if new_idx >= self.max_cycles:
            # Simulation has ended
            return False
        
        self.current_cycle_idx = new_idx
        return True
    
    def get_current_reading(self):
        """
        Get current cycle's sensor readings as dictionary.
        
        Returns:
            dict: {
                'engine_id': engine ID,
                'cycle': current cycle number,
                'sensor_*': sensor values for all active sensors,
                'op_setting_*': operational setting values,
                'timestamp_relative': relative time in cycles
            }
        """
        if self.current_cycle_idx >= self.max_cycles:
            return None
        
        row = self.df_engine.iloc[self.current_cycle_idx]
        
        # Extract sensor columns
        sensor_cols = [col for col in row.index if col.startswith('sensor_')]
        op_setting_cols = [col for col in row.index if col.startswith('op_setting_')]
        
        reading = {
            'engine_id': int(row['engine_id']),
            'cycle': int(row['cycle']),
            'timestamp_relative': self.current_cycle_idx
        }
        
        # Add sensor values
        for col in sensor_cols:
            if col in row.index:
                reading[col] = float(row[col])
        
        # Add operational settings
        for col in op_setting_cols:
            if col in row.index:
                reading[col] = float(row[col])
        
        # Add RUL if available
        if 'RUL' in row.index:
            reading['RUL_actual'] = int(row['RUL'])
        
        return reading
    
    def get_stream_history(self, n_last=50):
        """
        Get last N readings for time-series plotting.
        
        Returns:
            list of dicts: Last n_last readings
        """
        history = []
        for i in range(max(0, self.current_cycle_idx - n_last + 1), self.current_cycle_idx + 1):
            if i < len(self.df_engine):
                row = self.df_engine.iloc[i]
                sensor_cols = [col for col in row.index if col.startswith('sensor_')]
                
                reading = {
                    'cycle': int(row['cycle']),
                    'index': i
                }
                
                for col in sensor_cols:
                    if col in row.index:
                        reading[col] = float(row[col])
                
                history.append(reading)
        
        return history
    
    def get_current_rul_estimate(self, model=None, X_feature_cols=None):
        """
        Get RUL prediction for current reading using trained model.
        
        Args:
            model: Trained RUL prediction model
            X_feature_cols (list): Feature columns used by model
            
        Returns:
            float: Predicted RUL in cycles, or None if model/features unavailable
        """
        if model is None:
            model = self.model
        
        if model is None:
            return None
        
        current = self.get_current_reading()
        if current is None:
            return None
        
        # If feature columns provided, use them; otherwise try to infer
        if X_feature_cols:
            # Create feature vector from current reading
            X = np.array([[current.get(col, 0) for col in X_feature_cols]])
        else:
            # Try to use all sensor values
            sensor_vals = [v for k, v in current.items() if k.startswith('sensor_')]
            if not sensor_vals:
                return None
            X = np.array([sensor_vals])
        
        try:
            rul_pred = model.predict(X)[0]
            return max(0, float(rul_pred))  # Ensure non-negative
        except Exception as e:
            print(f"RUL prediction error: {e}")
            return None
    
    def is_fault_detected(self, rul_estimate=None, threshold=30):
        """
        Check if estimated RUL is below fault threshold.
        
        Args:
            rul_estimate (float): RUL prediction (uses model if None)
            threshold (int): RUL threshold for fault detection
            
        Returns:
            bool: True if fault detected (RUL < threshold)
        """
        if rul_estimate is None:
            rul_estimate = self.get_current_rul_estimate()
        
        if rul_estimate is None:
            return False
        
        return rul_estimate < threshold
    
    def get_engine_summary(self):
        """
        Get summary statistics for the simulated engine.
        
        Returns:
            dict: {
                'engine_id': engine ID,
                'total_cycles': total cycles available,
                'cycles_simulated': cycles processed so far,
                'progress_pct': percentage complete,
                'rul_at_start': RUL at first cycle,
                'rul_current': RUL at current cycle,
                'rul_final': RUL at last cycle
            }
        """
        first_row = self.df_engine.iloc[0]
        current_row = self.df_engine.iloc[min(self.current_cycle_idx, len(self.df_engine) - 1)]
        last_row = self.df_engine.iloc[-1]
        
        return {
            'engine_id': self.engine_id,
            'total_cycles': self.max_cycles,
            'cycles_simulated': self.current_cycle_idx + 1,
            'progress_pct': 100 * (self.current_cycle_idx + 1) / self.max_cycles,
            'rul_at_start': int(first_row.get('RUL', -1)),
            'rul_current': int(current_row.get('RUL', -1)),
            'rul_final': int(last_row.get('RUL', -1))
        }