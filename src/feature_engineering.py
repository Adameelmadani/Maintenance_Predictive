"""
Feature Engineering Module for Predictive Maintenance

Implements advanced feature extraction:
- Rolling windowed statistics (mean, std)
- Statistical features per cycle (RMS, Kurtosis, Peak-to-Peak, Skewness)
- Frequency domain analysis (FFT)
- Health index normalization
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.fft import fft


class FeatureEngineer:
    """
    Advanced feature extraction for turbofan engine sensor data.
    
    Extracts temporal, statistical, and frequency-domain features to improve
    ML model performance for RUL prediction.
    """
    
    def __init__(self, window_size=30):
        """
        Initialize FeatureEngineer.
        
        Args:
            window_size (int): Size of rolling window (default: 30 cycles)
        """
        self.window_size = window_size
    
    def add_rolling_features(self, df, window=None, sensors=None):
        """
        Add rolling window features (mean and std) for each sensor.
        
        Creates two new columns per sensor: sensor_X_rolling_mean, sensor_X_rolling_std
        
        Args:
            df (pd.DataFrame): Dataframe with sensor columns
            window (int): Rolling window size (uses self.window_size if None)
            sensors (list): List of sensor column names (auto-detects if None)
            
        Returns:
            pd.DataFrame: DataFrame with added rolling features
        """
        df = df.copy()
        if window is None:
            window = self.window_size
        
        # Auto-detect sensor columns
        if sensors is None:
            sensors = [col for col in df.columns if col.startswith('sensor_')]
        
        print(f"Adding rolling features (window={window}) for {len(sensors)} sensors...")
        
        for sensor in sensors:
            if sensor in df.columns:
                df[f'{sensor}_rolling_mean'] = df[sensor].rolling(window=window, min_periods=1).mean()
                df[f'{sensor}_rolling_std'] = df[sensor].rolling(window=window, min_periods=1).std().fillna(0)
        
        print(f"✓ Added {2 * len(sensors)} rolling features")
        return df
    
    def add_statistical_features(self, df, sensors=None):
        """
        Add statistical features per cycle: RMS, Kurtosis, Peak-to-Peak, Skewness.
        
        These are aggregate statistics across all sensors for each engine/cycle snapshot.
        
        Args:
            df (pd.DataFrame): Dataframe with sensor columns
            sensors (list): List of sensor column names (auto-detects if None)
            
        Returns:
            pd.DataFrame: DataFrame with added statistical features
        """
        df = df.copy()
        
        # Auto-detect sensor columns
        if sensors is None:
            sensors = [col for col in df.columns if col.startswith('sensor_') and '_rolling' not in col]
        
        print(f"Adding statistical features for {len(sensors)} sensors...")
        
        sensor_data = df[sensors].values  # shape: (n_samples, n_sensors)
        
        # RMS (Root Mean Square)
        df['rms'] = np.sqrt(np.mean(sensor_data ** 2, axis=1))
        
        # Kurtosis (measure of outliers/heavy tails)
        df['kurtosis'] = stats.kurtosis(sensor_data, axis=1)
        
        # Peak-to-Peak (max - min across sensors)
        df['peak_to_peak'] = np.ptp(sensor_data, axis=1)
        
        # Skewness (asymmetry of distribution)
        df['skewness'] = stats.skew(sensor_data, axis=1)
        
        print(f"✓ Added 4 statistical features: RMS, Kurtosis, Peak-to-Peak, Skewness")
        return df
    
    def compute_fft_spectrum(self, signal, fs=1.0, n_freq=10):
        """
        Compute FFT spectrum for frequency domain analysis.
        
        Args:
            signal (np.ndarray): 1D signal array
            fs (float): Sampling frequency (default: 1.0 Hz)
            n_freq (int): Number of top frequencies to return
            
        Returns:
            dict: {
                'frequencies': array of frequencies,
                'amplitudes': array of magnitudes,
                'top_freqs': top n_freq frequencies,
                'top_amps': corresponding amplitudes,
                'dominant_freq': most dominant frequency
            }
        """
        # Remove NaN values
        signal = signal[~np.isnan(signal)]
        
        # Compute FFT
        fft_values = fft(signal)
        magnitudes = np.abs(fft_values[:len(fft_values)//2])
        frequencies = np.fft.fftfreq(len(signal), 1/fs)[:len(fft_values)//2]
        
        # Find top frequencies
        top_indices = np.argsort(magnitudes)[-n_freq:][::-1]
        top_freqs = frequencies[top_indices]
        top_amps = magnitudes[top_indices]
        
        dominant_freq = top_freqs[0] if len(top_freqs) > 0 else 0
        
        return {
            'frequencies': frequencies,
            'amplitudes': magnitudes,
            'top_freqs': top_freqs,
            'top_amps': top_amps,
            'dominant_freq': dominant_freq
        }
    
    def compute_health_index(self, rul_actual, rul_predicted, method='normalized'):
        """
        Compute Health Index: normalized RUL prediction to 0-100% scale.
        
        Health Index = 100 * (1 - RUL_predicted / RUL_max)
        
        - 0% = Failed (RUL = 0)
        - 50% = Half-life remaining
        - 100% = Fully healthy (RUL = max_rul)
        
        Args:
            rul_actual (np.ndarray): Actual RUL values
            rul_predicted (np.ndarray): Predicted RUL values
            method (str): 'normalized' or 'confidence_adjusted'
            
        Returns:
            np.ndarray: Health index values (0-100%)
        """
        max_rul = np.max(rul_actual)
        
        if method == 'normalized':
            # Simple normalization
            health_index = 100 * (rul_predicted / max_rul)
        else:
            # Could add confidence-adjusted version later
            health_index = 100 * (rul_predicted / max_rul)
        
        # Clip to 0-100
        health_index = np.clip(health_index, 0, 100)
        
        return health_index
    
    def extract_all_features(self, df, window=30, sensors=None):
        """
        Extract all engineered features in one call.
        
        Convenience method that applies rolling, statistical, and other features.
        
        Args:
            df (pd.DataFrame): Input dataframe
            window (int): Rolling window size
            sensors (list): Sensor columns to use
            
        Returns:
            pd.DataFrame: DataFrame with all new features added
        """
        df = self.add_rolling_features(df, window=window, sensors=sensors)
        df = self.add_statistical_features(df, sensors=sensors)
        return df
