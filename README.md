# Predictive Maintenance System

A full-stack machine learning application for predicting remaining useful life (RUL) of turbofan engines and monitoring fleet health in real-time.

## Overview

This project implements a predictive maintenance platform using advanced machine learning models and signal processing techniques. It features a Flask REST API backend and a React-based interactive dashboard for visualizing engine health, predictions, and sensor data analysis.

**Key Capabilities:**
- Multi-model RUL prediction (5 regression algorithms)
- Real-time fleet health monitoring
- Advanced signal analysis (FFT, rolling statistics)
- Engine-specific diagnostics and maintenance prescriptions
- Model performance benchmarking

## Technology Stack

### Backend
- **Framework:** Flask 3.0+ with CORS support
- **ML Libraries:** scikit-learn, XGBoost, joblib
- **Data Processing:** pandas, NumPy
- **Signal Analysis:** SciPy (FFT, statistical functions)

### Frontend
- **Framework:** React 19.1.0
- **Build Tool:** Vite 6.0
- **Routing:** React Router DOM 7.15
- **Visualization:** Recharts 3.8.1
- **UI Components:** Lucide React

## Project Structure

```
.
├── api/
│   ├── app.py              # Flask application & API endpoints
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── src/
│   │   └── main.jsx        # React entry point
│   ├── index.html
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js
├── src/
│   ├── data_loader.py      # Data loading & preprocessing
│   ├── feature_engineering.py
│   ├── simulation.py
│   ├── alerts.py
│   └── models/
│       ├── regression.py   # RUL prediction models
│       ├── classification.py
│       └── model_utils.py
├── data/
│   ├── raw/CMaps/          # Raw turbofan engine datasets
│   └── processed/          # Preprocessed data & models
├── train_models.py         # Model training pipeline
└── models/                 # Trained model binaries (.pkl files)
```

## Installation

### Backend Setup

1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r api/requirements.txt
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start the Backend (Flask API)

```bash
python api/app.py
```

The API will be available at `http://localhost:5000`

### Start the Frontend (React Dashboard)

```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:5173` (or as shown in terminal)

## API Endpoints

### Fleet Overview
- `GET /api/overview` - Fleet statistics, health distribution, RUL histogram
- `GET /api/kpis` - Key performance indicators (availability, MTBF, OEE)
- `GET /api/engines` - List all engine IDs
- `GET /api/health` - Service health check

### Engine Details
- `GET /api/engine/<engine_id>` - Detailed engine data, multi-model predictions, prescriptions
- `GET /api/monitoring/<engine_id>?sensor=<sensor_name>&window=<window_size>` - Signal monitoring with FFT, rolling statistics, heatmap

### Model Management
- `POST /api/predict` - Get RUL prediction for specific engine and model
- `GET /api/benchmarks` - Model performance benchmarks (MAE, RMSE, R2 scores)

## Training Models

Run the complete training pipeline:

```bash
python train_models.py
```

This script:
1. Loads and preprocesses turbofan engine data (CMaps FD001 dataset)
2. Trains 5 RUL regression models (XGBoost, RandomForest, Huber, DecisionTree, MLP)
3. Trains 2 classification models (RandomForest, SVM)
4. Generates benchmark results
5. Saves all models to `models/` directory

Outputs:
- Processed datasets in `data/processed/`
- Trained models in `models/`
- Benchmark results in `models/benchmark_results.json`

## Data Format

The system uses the NASA Turbofan Engine Degradation Simulation (C-MAPSS) dataset:

**Input:** Raw sensor readings from 21 sensors across multiple engines over operational cycles

**Preprocessing:**
- Rolling window statistics (mean, std with 30-cycle window)
- Statistical features (RMS, Kurtosis, Peak-to-Peak, Skewness)
- Frequency domain analysis (FFT features)
- Health label classification (healthy, warning, critical)

## Model Performance

The API loads pre-trained models and compares their predictions:
- **XGBoost:** Best overall performance
- **RandomForest:** Fast, interpretable
- **Huber Regressor:** Robust to outliers
- **MLP:** Neural network approach
- **DecisionTree:** Baseline model

Metrics tracked: MAE, RMSE, R2 Score

## Dashboard Features

- **Home/Overview:** Fleet-wide KPIs, health distribution, engine status summary
- **Engine Details:** Individual engine RUL predictions, sensor data, health trends
- **Monitoring:** Real-time sensor signal analysis with FFT, rolling statistics
- **Model Comparison:** Side-by-side model predictions for validation
- **Alerts:** Status indicators (healthy, warning, critical) with maintenance prescriptions

## Health Status Definitions

- **Healthy** (RUL > 50): Normal operation, schedule regular checks
- **Warning** (30 < RUL <= 50): Order replacement parts, plan maintenance
- **Urgent** (15 < RUL <= 30): Schedule immediate maintenance
- **Critical** (RUL <= 15): Immediate shutdown recommended

## Configuration

### Backend Configuration
Edit `api/app.py` to adjust:
- Data directories and model paths
- Sensor columns and feature selection
- Health status thresholds
- Prediction bounds (0-125 cycles)

### Frontend Configuration
Edit `frontend/vite.config.js` for build settings
Edit `frontend/package.json` for dependency versions

## Performance Considerations

- **API Caching:** Models are loaded once at startup
- **Frontend Optimization:** React with Vite for fast builds and HMR
- **Data Handling:** Preprocessed datasets minimize computation
- **Signal Analysis:** FFT limited to top 10 frequencies for performance

## Development Workflow

1. Backend changes: Flask will auto-reload with debug=True
2. Frontend changes: Vite provides instant HMR (Hot Module Replacement)
3. Add new models: Update `train_models.py` and reload in `api/app.py`
4. Modify features: Update `src/feature_engineering.py` and retrain

## Troubleshooting

**API fails to start:**
- Check data files exist in `data/processed/`
- Verify model files in `models/` directory
- Run `python train_models.py` to regenerate models

**Frontend can't connect to API:**
- Ensure Flask is running on port 5000
- Check CORS headers in `api/app.py`
- Verify backend URL in frontend environment

**Slow predictions:**
- Check dataset size and model complexity
- Monitor system resources
- Consider caching prediction results

## Future Enhancements

- Database integration for historical tracking
- Real-time data streaming support
- Advanced anomaly detection
- Ensemble model voting
- Custom alert thresholds per engine
- Maintenance history integration

## License

This project is developed as part of the ENSAM (École Nationale Supérieure des Arts et Métiers) curriculum.

## References

- C-MAPSS Dataset: NASA Ames Prognostics CoE
- XGBoost: Chen & Guestrin (2016)
- PyTorch/scikit-learn documentation
- Flask & React best practices
