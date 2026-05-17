"""
Alert Management System for Predictive Maintenance

Generates maintenance alerts based on RUL predictions and health index,
with severity levels: WATCH, WARNING, CRITICAL.
Maintains event log for audit trail and historical analysis.
"""

from datetime import datetime
import pandas as pd


class AlertManager:
    """
    Manages alerts and maintenance recommendations based on engine health metrics.
    
    Maintains a log of all alerts with timestamps, severity levels, and recommended actions.
    """
    
    SEVERITY_LEVELS = {
        'INFO': 0,
        'WATCH': 1,
        'WARNING': 2,
        'CRITICAL': 3
    }
    
    def __init__(self):
        """Initialize alert manager with empty log."""
        self.log = []
    
    def check_and_trigger(self, rul_estimate, health_index=None, engine_id=None):
        """
        Check RUL and health metrics, determine if alert should be triggered.
        
        Alert Rules:
        - CRITICAL: RUL < 15 → "IMMEDIATE MAINTENANCE REQUIRED"
        - WARNING: 15 ≤ RUL < 30 → "Schedule maintenance within 30 cycles"
        - WATCH: 30 ≤ RUL < 50 → "Monitor closely"
        - INFO: RUL ≥ 50 → "Normal operation"
        
        Args:
            rul_estimate (float): Predicted RUL in cycles
            health_index (float): Health index (0-100%), optional
            engine_id (int): Engine ID, optional
            
        Returns:
            dict or None: Alert info if triggered, None if no alert
        """
        if rul_estimate is None or rul_estimate < 0:
            return None
        
        # Determine severity and message
        if rul_estimate < 15:
            severity = 'CRITICAL'
            message = f"IMMEDIATE MAINTENANCE REQUIRED - RUL = {rul_estimate:.1f} cycles"
            action = "SHUTDOWN RECOMMENDED - Reduce load immediately - Order parts urgently"
        elif rul_estimate < 30:
            severity = 'WARNING'
            message = f"URGENT MAINTENANCE - RUL = {rul_estimate:.1f} cycles"
            action = "Schedule maintenance within next 20 cycles - Notify maintenance team"
        elif rul_estimate < 50:
            severity = 'WATCH'
            message = f"MONITOR CLOSELY - RUL = {rul_estimate:.1f} cycles"
            action = "Monitor performance - Plan maintenance - Check for anomalies"
        else:
            severity = 'INFO'
            message = f"NORMAL OPERATION - RUL = {rul_estimate:.1f} cycles"
            action = "Continue normal operation - Next scheduled check in 40 cycles"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'engine_id': engine_id,
            'severity': severity,
            'rul': round(rul_estimate, 2),
            'health_index': round(health_index, 1) if health_index is not None else None,
            'message': message,
            'action': action
        }
    
    def add_log_entry(self, entry):
        """
        Add alert entry to log.
        
        Args:
            entry (dict): Alert entry with timestamp, engine_id, severity, etc.
        """
        if entry is not None:
            self.log.append(entry)
    
    def add_alert(self, rul_estimate, health_index=None, engine_id=None):
        """
        Check conditions and add alert to log if triggered.
        
        Args:
            rul_estimate (float): RUL prediction
            health_index (float): Health index
            engine_id (int): Engine ID
        """
        alert = self.check_and_trigger(rul_estimate, health_index, engine_id)
        if alert is not None:
            self.add_log_entry(alert)
    
    def get_log_as_dataframe(self):
        """
        Convert alert log to pandas DataFrame for display.
        
        Returns:
            pd.DataFrame: Alerts with columns for timestamp, engine_id, severity, RUL, message
        """
        if not self.log:
            return pd.DataFrame(columns=['timestamp', 'engine_id', 'severity', 'rul', 'health_index', 'message', 'action'])
        
        df = pd.DataFrame(self.log)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
        return df
    
    def get_active_alerts(self, severity_threshold='WATCH'):
        """
        Get current active alerts at or above threshold severity.
        
        Args:
            severity_threshold (str): Minimum severity level to return
            
        Returns:
            list: Active alerts
        """
        threshold_val = self.SEVERITY_LEVELS.get(severity_threshold, 0)
        
        return [alert for alert in self.log 
                if self.SEVERITY_LEVELS.get(alert.get('severity'), 0) >= threshold_val]
    
    def get_statistics(self):
        """
        Get summary statistics of all alerts.
        
        Returns:
            dict: {
                'total_alerts': count of alerts,
                'critical_count': count of CRITICAL alerts,
                'warning_count': count of WARNING alerts,
                'watch_count': count of WATCH alerts,
                'affected_engines': unique engines with alerts,
                'latest_alert': most recent alert timestamp
            }
        """
        if not self.log:
            return {
                'total_alerts': 0,
                'critical_count': 0,
                'warning_count': 0,
                'watch_count': 0,
                'affected_engines': 0,
                'latest_alert': None
            }
        
        df = self.get_log_as_dataframe()
        severity_counts = df['severity'].value_counts().to_dict()
        
        return {
            'total_alerts': len(self.log),
            'critical_count': severity_counts.get('CRITICAL', 0),
            'warning_count': severity_counts.get('WARNING', 0),
            'watch_count': severity_counts.get('WATCH', 0),
            'affected_engines': int(df['engine_id'].nunique()) if 'engine_id' in df.columns else 0,
            'latest_alert': df['timestamp'].max().isoformat() if 'timestamp' in df.columns else None
        }
    
    def get_alerts_by_severity(self):
        """
        Group alerts by severity level.
        
        Returns:
            dict: {
                'CRITICAL': [alerts],
                'WARNING': [alerts],
                'WATCH': [alerts]
            }
        """
        grouped = {
            'CRITICAL': [],
            'WARNING': [],
            'WATCH': [],
            'INFO': []
        }
        
        for alert in self.log:
            severity = alert.get('severity', 'INFO')
            if severity in grouped:
                grouped[severity].append(alert)
        
        return grouped
    
    def clear_old_logs(self, keep_recent_n=1000):
        """
        Remove older log entries to prevent memory bloat.
        
        Args:
            keep_recent_n (int): Number of recent entries to keep
        """
        if len(self.log) > keep_recent_n:
            self.log = self.log[-keep_recent_n:]
    
    def export_to_csv(self, filename):
        """
        Export alert log to CSV file.
        
        Args:
            filename (str): Output CSV file path
        """
        df = self.get_log_as_dataframe()
        df.to_csv(filename, index=False)
        print(f"Exported {len(df)} alerts to {filename}")