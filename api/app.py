"""
Flask API Backend for Predictive Maintenance React Dashboard

Serves data from trained models and preprocessed datasets via REST endpoints.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from scipy import stats
from scipy.fft import fft

app = Flask(__name__)
CORS(app)

# ============================================================================
# DATA LOADING
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data' / 'processed'
MODELS_DIR = BASE_DIR / 'models'

# Load processed data
df_train = pd.read_csv(DATA_DIR / 'train_processed.csv')
df_test = pd.read_csv(DATA_DIR / 'test_processed.csv')
X_test = np.load(DATA_DIR / 'X_test.npy')
y_rul_test = np.load(DATA_DIR / 'y_rul_test.npy')
y_rul_train = np.load(DATA_DIR / 'y_rul_train.npy')
X_train = np.load(DATA_DIR / 'X_train.npy')

# Load benchmark results
with open(MODELS_DIR / 'benchmark_results.json', 'r') as f:
    benchmark_results = json.load(f)

# Load models
models = {}
rul_model_names = ['huber', 'decisiontree', 'mlp', 'randomforest', 'xgboost']
display_names = {'huber': 'Huber', 'decisiontree': 'DecisionTree', 'mlp': 'MLP',
                 'randomforest': 'RandomForest', 'xgboost': 'XGBoost'}
for name in rul_model_names:
    path = MODELS_DIR / f'rul_{name}.pkl'
    if path.exists():
        models[display_names[name]] = joblib.load(path)

cls_model_names = ['randomforest', 'svm']
for name in cls_model_names:
    path = MODELS_DIR / f'cls_{name}.pkl'
    if path.exists():
        dname = 'RandomForest' if name == 'randomforest' else 'SVM'
        models[f'cls_{dname}'] = joblib.load(path)

# Sensor columns (excluding dropped and rolling)
sensor_cols = [col for col in df_test.columns if col.startswith('sensor_') and '_rolling' not in col]
feature_cols = [col for col in df_test.columns if col not in ['engine_id', 'cycle', 'RUL', 'health_label']]

print(f"[OK] Loaded {len(models)} models, {len(df_test)} test rows, {len(sensor_cols)} sensors")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_engine_data(engine_id):
    """Get test data for a specific engine."""
    return df_test[df_test['engine_id'] == engine_id].copy()


def predict_rul(model_name, features):
    """Get RUL prediction from a model."""
    model = models.get(model_name)
    if model is None:
        return None
    try:
        pred = model.predict(features)[0]
        return float(max(0, min(125, pred)))
    except Exception:
        return None


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'models_loaded': len(models)})


@app.route('/api/overview', methods=['GET'])
def overview():
    """Fleet overview data for the dashboard home."""
    engine_ids = sorted(df_test['engine_id'].unique())
    n_engines = len(engine_ids)

    fleet_data = []
    fleet_ruls = []

    for eid in engine_ids:
        edata = df_test[df_test['engine_id'] == eid]
        if len(edata) > 0:
            last_rul = float(edata.iloc[-1]['RUL'])
            fleet_ruls.append(last_rul)
            status = 'healthy' if last_rul > 50 else ('warning' if last_rul > 30 else 'critical')
            fleet_data.append({
                'engine_id': int(eid),
                'rul': last_rul,
                'status': status,
                'cycles': int(edata['cycle'].max()),
                'health_index': round(100 * last_rul / 125, 1)
            })

    avg_health = 100 * (np.mean(fleet_ruls) / 125) if fleet_ruls else 100
    min_rul = min(fleet_ruls) if fleet_ruls else 0
    critical_count = sum(1 for r in fleet_ruls if r <= 30)
    warning_count = sum(1 for r in fleet_ruls if 30 < r <= 50)
    healthy_count = sum(1 for r in fleet_ruls if r > 50)

    # RUL distribution histogram
    rul_bins = [0, 15, 30, 50, 75, 100, 125]
    rul_hist, _ = np.histogram(fleet_ruls, bins=rul_bins)

    return jsonify({
        'fleet_health': round(avg_health, 1),
        'min_rul': round(min_rul, 1),
        'total_engines': n_engines,
        'critical_count': critical_count,
        'warning_count': warning_count,
        'healthy_count': healthy_count,
        'engines': fleet_data,
        'rul_distribution': {
            'bins': ['0-15', '15-30', '30-50', '50-75', '75-100', '100-125'],
            'counts': rul_hist.tolist()
        },
        'train_samples': len(df_train),
        'test_samples': len(df_test),
        'n_features': len(feature_cols),
        'models_loaded': len([m for m in models if not m.startswith('cls_')])
    })


@app.route('/api/kpis', methods=['GET'])
def kpis():
    """KPI metrics for the dashboard."""
    engine_ids = sorted(df_test['engine_id'].unique())
    fleet_ruls = []
    status_counts = {'healthy': 0, 'warning': 0, 'critical': 0}

    for eid in engine_ids:
        edata = df_test[df_test['engine_id'] == eid]
        if len(edata) > 0:
            last_rul = float(edata.iloc[-1]['RUL'])
            fleet_ruls.append(last_rul)
            if last_rul > 50:
                status_counts['healthy'] += 1
            elif last_rul > 30:
                status_counts['warning'] += 1
            else:
                status_counts['critical'] += 1

    fleet_ruls_arr = np.array(fleet_ruls)
    avg_rul = float(np.mean(fleet_ruls_arr))
    median_rul = float(np.median(fleet_ruls_arr))
    std_rul = float(np.std(fleet_ruls_arr))

    # MTBF estimate (mean time between failures approximation)
    mtbf_estimate = avg_rul * 1.5  # Rough estimate

    # Availability rate
    availability = 100 * (1 - status_counts['critical'] / len(engine_ids))

    # Best model performance from benchmarks
    rul_benchmarks = benchmark_results.get('RUL_Models', {}).get('benchmarks', {})
    best_model = min(rul_benchmarks.items(), key=lambda x: x[1]['MAE']) if rul_benchmarks else ('N/A', {'MAE': 0})

    # OEE-like metric (simplified)
    oee = availability * (avg_rul / 125) * 0.95  # availability * performance * quality

    return jsonify({
        'fleet_availability': round(availability, 1),
        'avg_rul': round(avg_rul, 1),
        'median_rul': round(median_rul, 1),
        'std_rul': round(std_rul, 1),
        'mtbf_estimate': round(mtbf_estimate, 1),
        'oee': round(oee, 1),
        'status_distribution': status_counts,
        'total_engines': len(engine_ids),
        'best_model': {'name': best_model[0], 'mae': best_model[1]['MAE']},
        'prediction_accuracy': round(100 - best_model[1]['MAE'] / 125 * 100, 1),
        'engines_at_risk': status_counts['critical'] + status_counts['warning'],
        'maintenance_due': status_counts['critical'],
        'sensor_count': len(sensor_cols),
        'data_points': len(df_test)
    })


@app.route('/api/engines', methods=['GET'])
def get_engines():
    """List all engine IDs."""
    ids = sorted(df_test['engine_id'].unique().tolist())
    return jsonify({'engine_ids': [int(i) for i in ids]})


@app.route('/api/engine/<int:engine_id>', methods=['GET'])
def get_engine_detail(engine_id):
    """Get detailed data for a specific engine."""
    edata = get_engine_data(engine_id)
    if len(edata) == 0:
        return jsonify({'error': f'Engine {engine_id} not found'}), 404

    last_row = edata.iloc[-1]
    last_rul = float(last_row['RUL'])
    health_index = round(100 * last_rul / 125, 1)

    # Sensor time series (last 100 cycles)
    recent = edata.tail(100)
    sensor_series = {}
    for col in sensor_cols:
        if col in recent.columns:
            sensor_series[col] = recent[col].tolist()

    # Multi-model predictions
    predictions = {}
    X_current = np.array([[last_row.get(col, 0) for col in feature_cols]])
    for mname, mobj in models.items():
        if not mname.startswith('cls_'):
            pred = predict_rul(mname, X_current)
            if pred is not None:
                predictions[mname] = round(pred, 1)

    # Determine status
    status = 'healthy' if last_rul > 50 else ('warning' if last_rul > 30 else 'critical')

    # Prescription
    if last_rul > 50:
        prescription = {'status': 'NORMAL', 'action': 'Continue normal operation', 'risk': 'Low', 'next_check': '40 cycles'}
    elif last_rul > 30:
        prescription = {'status': 'PLAN MAINTENANCE', 'action': 'Order replacement parts', 'risk': 'Medium', 'next_check': '20 cycles'}
    elif last_rul > 15:
        prescription = {'status': 'URGENT MAINTENANCE', 'action': 'Schedule immediate maintenance', 'risk': 'High', 'next_check': 'ASAP'}
    else:
        prescription = {'status': 'CRITICAL SHUTDOWN', 'action': 'Immediate shutdown recommended', 'risk': 'Critical', 'next_check': 'EMERGENCY'}

    return jsonify({
        'engine_id': int(engine_id),
        'rul': last_rul,
        'health_index': health_index,
        'status': status,
        'total_cycles': int(edata['cycle'].max()),
        'current_cycle': int(last_row['cycle']),
        'predictions': predictions,
        'prescription': prescription,
        'sensor_series': sensor_series,
        'cycles': recent['cycle'].tolist(),
        'rul_history': recent['RUL'].tolist()
    })


@app.route('/api/monitoring/<int:engine_id>', methods=['GET'])
def monitoring(engine_id):
    """Signal monitoring data for a specific engine."""
    sensor = request.args.get('sensor', sensor_cols[0] if sensor_cols else 'sensor_2')
    window = int(request.args.get('window', 30))

    edata = get_engine_data(engine_id)
    if len(edata) == 0:
        return jsonify({'error': f'Engine {engine_id} not found'}), 404

    if sensor not in edata.columns:
        return jsonify({'error': f'Sensor {sensor} not found'}), 404

    signal = edata[sensor].values
    cycles = edata['cycle'].values.tolist()

    # Rolling stats
    df_temp = pd.DataFrame({'signal': signal})
    rolling_mean = df_temp['signal'].rolling(window=window, min_periods=1).mean().tolist()
    rolling_std = df_temp['signal'].rolling(window=window, min_periods=1).std().fillna(0).tolist()

    # Statistical indicators
    rms = float(np.sqrt(np.mean(signal ** 2)))
    kurtosis = float(stats.kurtosis(signal))
    p2p = float(np.ptp(signal))
    skewness = float(stats.skew(signal))

    # FFT
    clean_signal = signal[~np.isnan(signal)]
    fft_values = fft(clean_signal)
    magnitudes = np.abs(fft_values[:len(fft_values) // 2])
    frequencies = np.fft.fftfreq(len(clean_signal), 1.0)[:len(fft_values) // 2]
    top_indices = np.argsort(magnitudes)[-10:][::-1]
    top_freqs = frequencies[top_indices].tolist()
    top_amps = magnitudes[top_indices].tolist()

    # Heatmap data (last 50 cycles)
    last_50 = edata.tail(50)
    heatmap = {}
    for col in sensor_cols:
        if col in last_50.columns:
            heatmap[col] = last_50[col].tolist()

    # RUL threshold cycle
    rul_threshold_cycle = None
    if 'RUL' in edata.columns:
        threshold_data = edata[edata['RUL'] <= 30]
        if len(threshold_data) > 0:
            rul_threshold_cycle = int(threshold_data['cycle'].min())

    return jsonify({
        'engine_id': int(engine_id),
        'sensor': sensor,
        'cycles': cycles,
        'signal': signal.tolist(),
        'rolling_mean': rolling_mean,
        'rolling_std': rolling_std,
        'stats': {'rms': round(rms, 4), 'kurtosis': round(kurtosis, 4),
                  'peak_to_peak': round(p2p, 4), 'skewness': round(skewness, 4)},
        'fft': {'top_freqs': top_freqs, 'top_amps': top_amps,
                'frequencies': frequencies.tolist()[:50],
                'amplitudes': magnitudes.tolist()[:50]},
        'heatmap': heatmap,
        'rul_threshold_cycle': rul_threshold_cycle,
        'available_sensors': sensor_cols
    })


@app.route('/api/benchmarks', methods=['GET'])
def benchmarks():
    """Model benchmark results."""
    return jsonify(benchmark_results)


@app.route('/api/predict', methods=['POST'])
def predict():
    """Get RUL prediction for a given engine at current state."""
    data = request.json
    engine_id = data.get('engine_id', 1)
    model_name = data.get('model', 'XGBoost')

    edata = get_engine_data(engine_id)
    if len(edata) == 0:
        return jsonify({'error': f'Engine {engine_id} not found'}), 404

    last_row = edata.iloc[-1]
    X_current = np.array([[last_row.get(col, 0) for col in feature_cols]])
    pred = predict_rul(model_name, X_current)

    return jsonify({
        'engine_id': int(engine_id),
        'model': model_name,
        'predicted_rul': round(pred, 1) if pred else None,
        'actual_rul': float(last_row['RUL']),
        'health_index': round(100 * pred / 125, 1) if pred else None
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
