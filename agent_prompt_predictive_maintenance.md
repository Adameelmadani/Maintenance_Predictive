# 🤖 Claude Agent Prompt — Plateforme Intégrée de Maintenance Prédictive par l'IA
**ENSAM Meknès – 4ème Année IA | Prof. ZAKI Smail**

---

## 🎯 MISSION OVERVIEW

You are a senior AI/ML engineer and full-stack Python developer. Your task is to build, from scratch, a **complete AI-powered Predictive Maintenance Platform** using Python and Streamlit. The platform must cover the full pipeline: data ingestion → feature engineering → ML/DL training → real-time simulation → interactive dashboard with diagnostics, prognostics, and prescriptive insights.

This is a **4th-year AI engineering capstone project** — the code must be clean, modular, well-documented, and production-quality. Every component described below is **mandatory**.

---

## 📦 DATASET — NASA C-MAPSS (Turbofan Engine Degradation)

**Kaggle Link:** https://www.kaggle.com/datasets/behrad3d/nasa-cmaps

**Download instructions for the agent:**
```bash
pip install kaggle
kaggle datasets download -d behrad3d/nasa-cmaps
unzip nasa-cmaps.zip -d data/
```

**Dataset Structure:**
- Files: `train_FD001.txt`, `test_FD001.txt`, `RUL_FD001.txt` (use FD001 as primary; optionally support FD002–FD004)
- 26 columns (space-separated, no headers): `[engine_id, cycle, op_setting_1, op_setting_2, op_setting_3, sensor_1 … sensor_21]`
- Each row = one operational cycle snapshot of one engine
- Training set: engines run to failure; test set: engines stopped before failure
- Target: **RUL** (Remaining Useful Life) = cycles until failure

**Preprocessing rules (apply these exactly):**
1. Add column names manually (no header in raw file).
2. Drop constant/near-zero-variance sensors: `sensor_1`, `sensor_5`, `sensor_6`, `sensor_10`, `sensor_16`, `sensor_18`, `sensor_19`.
3. Compute RUL for training set: `RUL = max_cycle_per_engine - current_cycle`.
4. Apply **piecewise linear RUL clipping** at 125 cycles (standard CMAPSS practice).
5. Normalize with `StandardScaler` (fit on train, transform test).
6. Create **rolling window features** (window=30 cycles): rolling mean and rolling std for each sensor.
7. Extract statistical features per engine snapshot: **RMS**, **Kurtosis**, **Peak-to-Peak**, **Skewness**.
8. Create a **binary health label**: `0 = Healthy` (RUL > 30), `1 = Degraded/Faulty` (RUL ≤ 30).

---

## 🗂️ PROJECT STRUCTURE

Build the following exact folder/file structure:

```
predictive_maintenance/
│
├── data/                          # Raw and processed datasets
│   ├── raw/                       # Downloaded NASA CMAPSS files
│   └── processed/                 # Saved preprocessed CSVs
│
├── models/                        # Saved trained model files (.pkl, .h5)
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Data loading & preprocessing pipeline
│   ├── feature_engineering.py     # Statistical & frequency features
│   ├── models/
│   │   ├── __init__.py
│   │   ├── classification.py      # Diagnostic models (RF, SVM)
│   │   ├── regression.py          # Prognostic models (Huber, DT, MLP, RF, XGB)
│   │   └── model_utils.py         # Train/evaluate/save/load utilities
│   ├── simulation.py              # Real-time data stream simulator
│   └── alerts.py                  # Alert & notification logic
│
├── pages/                         # Streamlit multi-page app pages
│   ├── 1_🏠_Overview.py
│   ├── 2_📡_Monitoring_Signal.py
│   ├── 3_🧪_IA_Lab_Benchmark.py
│   ├── 4_🔮_Pronostic_RUL.py
│   └── 5_📋_Log_Maintenance.py
│
├── app.py                         # Main Streamlit entry point
├── train_models.py                # Standalone script: trains & saves all models
├── requirements.txt
└── README.md
```

---

## ⚙️ STEP 1 — `requirements.txt`

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
tensorflow>=2.13.0
plotly>=5.18.0
scipy>=1.11.0
joblib>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
streamlit-extras>=0.3.0
streamlit-autorefresh>=1.0.0
```

---

## ⚙️ STEP 2 — `src/data_loader.py`

Write a `DataLoader` class with these methods:
- `load_raw(filepath, set_type)` → loads raw `.txt` file, adds column names
- `compute_rul(df)` → computes RUL column for training data
- `clip_rul(df, clip=125)` → piecewise linear clipping
- `label_health(df, threshold=30)` → adds binary `health_label` column
- `normalize(df_train, df_test)` → fits StandardScaler on train, returns both normalized
- `get_processed_data()` → full pipeline returning `(X_train, y_rul_train, y_cls_train, X_test, y_rul_test)`

---

## ⚙️ STEP 3 — `src/feature_engineering.py`

Write a `FeatureEngineer` class:
- `add_rolling_features(df, window=30)` → rolling mean + rolling std per sensor
- `add_statistical_features(df)` → per-engine per-cycle: RMS, Kurtosis, Peak-to-Peak, Skewness
- `compute_fft_spectrum(signal, fs=1.0)` → returns frequencies & amplitudes (for FFT display)
- `compute_health_index(df, model)` → normalizes RUL prediction to 0–100% score

---

## ⚙️ STEP 4 — `src/models/regression.py` — The 5 Prognostic Models

Implement a `RULModelSuite` class that trains and evaluates all 5 models:

### Model 1 — Huber Regressor (Baseline Linear)
```python
from sklearn.linear_model import HuberRegressor
# epsilon=1.35, max_iter=300
# IMPORTANT: requires StandardScaler (already applied in data_loader)
```

### Model 2 — Decision Tree Regressor
```python
from sklearn.tree import DecisionTreeRegressor
# max_depth=8, min_samples_split=20, random_state=42
```

### Model 3 — MLP Regressor (Neural Network)
```python
from sklearn.neural_network import MLPRegressor
# hidden_layer_sizes=(128, 64, 32), activation='relu'
# max_iter=500, early_stopping=True, random_state=42
```

### Model 4 — Random Forest Regressor
```python
from sklearn.ensemble import RandomForestRegressor
# n_estimators=200, max_depth=12, n_jobs=-1, random_state=42
```

### Model 5 — XGBoost Regressor
```python
from xgboost import XGBRegressor
# n_estimators=300, max_depth=6, learning_rate=0.05
# subsample=0.8, colsample_bytree=0.8, random_state=42
```

**For each model, compute and store:**
- `MAE`, `RMSE`, `R²` on test set
- Predicted vs actual RUL arrays (for plotting)
- Training time (seconds)
- Save to `models/rul_{model_name}.pkl`

**Also implement `predict_with_confidence(model, X, n_bootstrap=100)`:**
- Bootstrap resampling to produce a **confidence interval** (5th–95th percentile)
- Return: `(y_pred, lower_bound, upper_bound)`

---

## ⚙️ STEP 5 — `src/models/classification.py` — Diagnostic Module

Implement a `DiagnosticModelSuite` class:

### Classifier 1 — Random Forest Classifier
```python
from sklearn.ensemble import RandomForestClassifier
# n_estimators=200, class_weight='balanced', random_state=42
```

### Classifier 2 — SVM
```python
from sklearn.svm import SVC
# kernel='rbf', C=10, gamma='scale', probability=True
```

**For each classifier, compute and store:**
- Accuracy, Precision, Recall, F1-score
- Full **confusion matrix** (for display)
- Classification report
- Save to `models/cls_{model_name}.pkl`

---

## ⚙️ STEP 6 — `train_models.py`

A standalone script that:
1. Loads and preprocesses data
2. Trains all 5 regression models + 2 classification models
3. Prints a comparison table (MAE, RMSE, R², training time)
4. Saves all models and a `models/benchmark_results.json` with all metrics
5. Prints "✅ All models trained and saved successfully."

---

## ⚙️ STEP 7 — `src/simulation.py`

Implement a `DataStreamSimulator` class that mimics a real-time sensor stream:

```python
class DataStreamSimulator:
    def __init__(self, df_test, engine_id=1, speed_factor=1):
        # Selects one engine's test sequence
        # speed_factor controls how fast cycles advance
    
    def get_current_reading(self):
        # Returns current cycle's sensor readings as dict
    
    def advance(self):
        # Move to next cycle (called every N seconds in Streamlit)
    
    def get_stream_history(self, n_last=50):
        # Returns last N readings for time-series plotting
    
    def get_current_rul_estimate(self, model):
        # Runs model inference on current reading
    
    def is_fault_detected(self, threshold=30):
        # Returns True if estimated RUL < threshold
    
    def reset(self):
        # Restart stream from beginning
```

---

## ⚙️ STEP 8 — `src/alerts.py`

Implement alert management:

```python
class AlertManager:
    def __init__(self):
        self.log = []  # list of dicts: {timestamp, engine_id, severity, message, action}
    
    def check_and_trigger(self, rul_estimate, health_index, engine_id):
        # CRITICAL if RUL < 15 → "IMMEDIATE MAINTENANCE REQUIRED"
        # WARNING if RUL < 30 → "Schedule maintenance within 30 cycles"
        # WATCH if RUL < 50 → "Monitor closely"
        # Returns severity string or None
    
    def add_log_entry(self, entry):
        ...
    
    def get_log_as_dataframe(self):
        ...
    
    def get_active_alerts(self):
        ...
```

---

## ⚙️ STEP 9 — THE STREAMLIT DASHBOARD (CRITICAL — MAKE IT EXCEPTIONAL)

### Global Design System (apply everywhere)

```python
# In app.py and every page, inject this custom CSS:
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

:root {
    --bg-primary: #0A0E1A;
    --bg-card: #0F1629;
    --bg-card2: #141B2D;
    --accent-cyan: #00D4FF;
    --accent-green: #00FF88;
    --accent-orange: #FF6B35;
    --accent-red: #FF3366;
    --accent-purple: #7B2FBE;
    --text-primary: #E8F4FD;
    --text-secondary: #8899AA;
    --border-glow: rgba(0, 212, 255, 0.3);
}

.stApp { background: var(--bg-primary); font-family: 'Rajdhani', sans-serif; }
h1, h2, h3 { font-family: 'Orbitron', monospace; color: var(--accent-cyan); }

/* Glowing metric cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-glow);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.1), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: all 0.3s ease;
}
.metric-card:hover { box-shadow: 0 0 35px rgba(0, 212, 255, 0.25); transform: translateY(-2px); }

/* Status badges */
.badge-healthy { background: rgba(0,255,136,0.15); color: #00FF88; border: 1px solid #00FF88; border-radius: 20px; padding: 4px 14px; font-weight: 700; }
.badge-warning { background: rgba(255,107,53,0.15); color: #FF6B35; border: 1px solid #FF6B35; border-radius: 20px; padding: 4px 14px; font-weight: 700; }
.badge-critical { background: rgba(255,51,102,0.15); color: #FF3366; border: 1px solid #FF3366; border-radius: 20px; padding: 4px 14px; font-weight: 700; animation: pulse 1.5s infinite; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Sidebar styling */
[data-testid="stSidebar"] { background: var(--bg-card2) !important; border-right: 1px solid var(--border-glow); }

/* All plotly charts: transparent background */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)
```

**All Plotly charts must use this template:**
```python
PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,22,41,0.8)",
    font=dict(family="Rajdhani, sans-serif", color="#E8F4FD"),
    colorway=["#00D4FF", "#00FF88", "#FF6B35", "#FF3366", "#7B2FBE"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=True, linecolor="rgba(0,212,255,0.3)"),
)
```

---

### PAGE 1 — `pages/1_🏠_Overview.py` — "Mission Control"

**Layout:** Full-width dark dashboard with a top status bar and 3 columns below.

**Content:**

1. **Top Header Banner:**
   - Title: `⚡ PREDICTIVE MAINTENANCE — MISSION CONTROL`
   - Subtitle: `NASA C-MAPSS Turbofan Fleet | Real-Time AI Monitoring`
   - Live clock (use `streamlit-autorefresh` to refresh every 2 seconds)

2. **Fleet Status Row (use `st.columns(5)`):**
   - One glowing colored circle per engine (engines 1–5 from test set)
   - Green = Healthy (RUL > 50), Orange = Warning (30 < RUL ≤ 50), Red = Critical (RUL ≤ 30)
   - Show engine ID + estimated RUL under each circle
   - Implemented as custom HTML/CSS injected via `st.markdown`

3. **KPI Metrics Row (`st.columns(4)`):**
   - 🟢 Fleet Health Index (average across all engines, 0–100%)
   - ⏱️ Lowest RUL in Fleet (most urgent engine)
   - ⚠️ Active Alerts count
   - 🔧 Engines in Critical Zone

4. **Two-column section:**
   - LEFT: Plotly gauge chart (big semi-circular gauge) showing current fleet health %
     - Green zone: 70–100%, Orange: 40–70%, Red: 0–40%
   - RIGHT: Plotly bar chart — "RUL Distribution by Engine" (horizontal bars, color-coded by severity)

5. **Bottom: Recent Alerts Preview** — last 3 alerts from `AlertManager` displayed as styled cards

---

### PAGE 2 — `pages/2_📡_Monitoring_Signal.py` — "Signal Analysis"

**Sidebar controls:**
- `st.selectbox` → choose engine (1–5)
- `st.selectbox` → choose sensor (from the 14 remaining sensors after dropping constants)
- `st.slider` → window size for rolling average (5–50)
- `st.toggle` → "Live Simulation Mode" (uses `streamlit-autorefresh`)

**Main content:**

1. **Raw Signal Time Series (full width):**
   - Plotly `go.Scatter` — sensor value over cycles
   - Overlay: rolling mean (dashed cyan line)
   - Shaded area between ±1 std (semi-transparent)
   - Vertical red dashed line at RUL=30 threshold if applicable

2. **Statistical Indicators Row (`st.columns(4)`):**
   - RMS value (with delta from previous 10 cycles)
   - Kurtosis (with interpretation: >3 = heavy tails → anomaly risk)
   - Peak-to-Peak
   - Skewness
   - Each as a styled `st.metric` card with colored delta arrows

3. **FFT Spectrum (full width):**
   - Compute FFT on the selected sensor signal using `np.fft.fft`
   - Plot as Plotly bar chart (frequency domain)
   - Highlight dominant frequency with annotation
   - Label: "Dominant Frequency: X Hz — [Normal / Anomalous]"

4. **Multi-sensor Heatmap:**
   - Plotly `px.imshow` — rows=sensors, columns=last 50 cycles, color=normalized value
   - Title: "Sensor Correlation Heatmap (Last 50 Cycles)"

---

### PAGE 3 — `pages/3_🧪_IA_Lab_Benchmark.py` — "AI Lab"

**This page benchmarks all 5 RUL models and 2 classifiers.**

1. **Model Selection Tabs:** Use `st.tabs(["📈 Regression Models", "🎯 Classification Models"])`

**TAB 1 — Regression (RUL Prediction):**

   a. **Performance Comparison Table** (all 5 models):
      - Columns: Model Name | MAE | RMSE | R² | Training Time | Rank
      - Highlight best model in each metric with a green background
      - Load from `models/benchmark_results.json`

   b. **Radar/Spider Chart** (Plotly `go.Scatterpolar`):
      - One trace per model, normalized metrics on axes: [MAE_inv, RMSE_inv, R², Speed]
      - Title: "Model Performance Radar"

   c. **Predicted vs Actual Plot** for selected model:
      - `st.selectbox` → pick model
      - Plotly scatter: x=actual RUL, y=predicted RUL
      - Red diagonal line (perfect prediction)
      - Points colored by error magnitude (colorscale Viridis)

   d. **Residuals Distribution:**
      - Plotly histogram of (predicted - actual) per model
      - Vertical line at 0, shaded region ±15 cycles (acceptable error zone)

**TAB 2 — Classification (Diagnostic):**

   a. **Confusion Matrix** (Plotly `go.Heatmap`):
      - For both RF and SVM side by side (`st.columns(2)`)
      - Annotations showing TP/TN/FP/FN counts
      - Color: green=correct, red=errors

   b. **Metrics Cards:**
      - Accuracy, Precision, Recall, F1 as `st.metric` widgets

   c. **ROC Curve** (Plotly):
      - Both classifiers on same plot
      - AUC annotated in legend
      - Dashed diagonal baseline

---

### PAGE 4 — `pages/4_🔮_Pronostic_RUL.py` — "Prognostic Center"

**This is the most visually impressive page.**

**Sidebar:**
- `st.selectbox` → choose engine
- `st.selectbox` → choose active model (default: XGBoost)
- `st.slider` → simulation speed (0.5x – 5x)
- `st.button` → "▶ Start Simulation" / "⏸ Pause" / "🔄 Reset"
- `st.toggle` → Show confidence interval

**Main content:**

1. **Health Index Gauge (top center, full width attention element):**
   - Giant animated Plotly gauge (0–100%)
   - Color zones: 0–30 = red (CRITICAL), 30–60 = orange (WARNING), 60–100 = green (HEALTHY)
   - Current value displayed large in center
   - Needle animation updates every refresh

2. **RUL Countdown Display:**
   - Large styled HTML metric: "⏱ TIME TO FAILURE: **XX CYCLES**"
   - With confidence interval: "95% CI: [lower — upper]"
   - Color changes: green → orange → red as RUL decreases

3. **Health Index Evolution (full width line chart):**
   - Plotly `go.Scatter` — Health Index (%) over cycles
   - Add projected future trend (dashed line extrapolation)
   - Shaded confidence band around projection
   - Vertical red line marking "critical threshold"
   - Annotation arrow pointing to "Predicted Failure Point"

4. **Multi-model RUL Comparison (below):**
   - All 5 models' RUL estimates at the current cycle
   - Plotly horizontal bar chart, sorted by estimate
   - Highlight selected active model

5. **Prescription Module (collapsible `st.expander`):**
   Based on current RUL estimate, display a structured maintenance recommendation:
   - **RUL > 50:** "✅ No action required. Next scheduled check in 40 cycles."
   - **30 < RUL ≤ 50:** "⚠️ Plan maintenance. Order replacement parts. Estimated intervention: within 20 cycles."
   - **15 < RUL ≤ 30:** "🔴 Schedule urgent maintenance. Notify maintenance team. Reduce operational load by 20%."
   - **RUL ≤ 15:** "🚨 IMMEDIATE SHUTDOWN RECOMMENDED. Critical failure imminent."
   - Show as styled card with color border matching severity

---

### PAGE 5 — `pages/5_📋_Log_Maintenance.py` — "Event Log"

1. **Filters row (st.columns(3)):**
   - Date range picker
   - Severity filter (ALL / CRITICAL / WARNING / WATCH)
   - Engine ID filter

2. **Event Log Table:**
   - `st.dataframe` with colored rows (use Pandas `Styler`)
   - Columns: Timestamp | Engine ID | Severity | RUL at Detection | Message | Recommended Action
   - Critical rows = red background, Warning = orange, Watch = yellow

3. **Alert Timeline Chart:**
   - Plotly Gantt-style or scatter timeline
   - x=cycle/time, y=engine_id, color=severity
   - Shows alert history visually

4. **Statistics Panel:**
   - `st.columns(3)`: Total alerts | MTBF estimate | Most problematic engine
   - Bar chart: alerts by engine
   - Pie chart: alerts by severity

5. **Export Button:**
   - `st.download_button` → export log as CSV

---

### `app.py` — Main Entry Point

```python
import streamlit as st

st.set_page_config(
    page_title="PredMaint AI | ENSAM Meknès",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS (full design system as shown above)
# Load and cache all models + preprocessed data at startup using @st.cache_resource
# Initialize session state: simulator, alert_manager, current_cycle, etc.
# Sidebar: show logo + navigation hints + global engine selector + last refresh time
```

**Session state variables to initialize:**
```python
st.session_state.setdefault("simulator", None)
st.session_state.setdefault("alert_manager", AlertManager())
st.session_state.setdefault("active_model_name", "XGBoost")
st.session_state.setdefault("current_engine", 1)
st.session_state.setdefault("simulation_running", False)
st.session_state.setdefault("cycle_index", 0)
```

---

## ⚙️ STEP 10 — CACHING STRATEGY (CRITICAL FOR PERFORMANCE)

```python
@st.cache_resource
def load_all_models():
    # Load all 7 saved model files from models/
    # Return dict: {"XGBoost": model, "RandomForest": model, ...}

@st.cache_data
def load_processed_data():
    # Load preprocessed CSVs from data/processed/
    # Return X_train, y_rul_train, X_test, y_rul_test, df_full

@st.cache_data
def load_benchmark_results():
    # Load models/benchmark_results.json
    # Return as DataFrame
```

---

## ⚙️ STEP 11 — `README.md`

Write a complete README with:
1. Project description & architecture diagram (ASCII)
2. Installation instructions: `pip install -r requirements.txt`
3. Dataset download instructions (Kaggle API command)
4. Training command: `python train_models.py`
5. Run dashboard: `streamlit run app.py`
6. Description of each page and each model
7. Performance results table (populated after training)
8. Known limitations & future improvements

---

## 🔄 IMPLEMENTATION ORDER (Follow this exactly)

**Phase 1 — Foundation:**
1. Create folder structure
2. Write `requirements.txt`
3. Write `src/data_loader.py` + test it on FD001
4. Write `src/feature_engineering.py`

**Phase 2 — Models:**
5. Write `src/models/regression.py` (all 5 models)
6. Write `src/models/classification.py` (RF + SVM)
7. Write `src/models/model_utils.py`
8. Write and run `train_models.py` → verify all models saved + benchmark_results.json generated

**Phase 3 — Simulation & Alerts:**
9. Write `src/simulation.py`
10. Write `src/alerts.py`

**Phase 4 — Dashboard:**
11. Write `app.py` with global CSS + session state + caching
12. Write Page 1 (Overview)
13. Write Page 2 (Monitoring Signal)
14. Write Page 3 (IA Lab Benchmark)
15. Write Page 4 (Pronostic RUL) — most time here
16. Write Page 5 (Log & Maintenance)

**Phase 5 — Polish:**
17. Write `README.md`
18. Test full end-to-end flow: download data → train → run dashboard
19. Fix any import errors, cache issues, or layout bugs

---

## ✅ QUALITY CHECKLIST (Verify before finishing)

- [ ] All 5 regression models train without errors and produce MAE/RMSE/R²
- [ ] All 2 classification models produce confusion matrices and ROC curves
- [ ] `benchmark_results.json` is generated correctly
- [ ] Streamlit app launches with `streamlit run app.py` without import errors
- [ ] All 5 pages load without errors
- [ ] Live simulation updates visually on Page 4
- [ ] Alert system logs entries correctly
- [ ] FFT spectrum plot renders on Page 2
- [ ] Confidence interval displays on Page 4
- [ ] Export CSV works on Page 5
- [ ] No hardcoded paths — all paths relative to project root
- [ ] All models loadable from disk after `train_models.py` completes
- [ ] CSS design system applied consistently on all pages
- [ ] `@st.cache_resource` used for model loading (no reloading on every interaction)

---

## 🚫 STRICT RULES

1. **Do NOT use placeholder/dummy data** — everything must use real NASA C-MAPSS FD001 data.
2. **Do NOT skip any of the 5 pages** — all are mandatory.
3. **Do NOT use Streamlit's default styling** — the custom CSS must be applied.
4. **Do NOT use `st.pyplot()`** — use Plotly exclusively for all charts.
5. **Do NOT use `st.experimental_*`** — use stable APIs only.
6. **Every function must have a docstring** explaining its inputs, outputs, and purpose.
7. **Every model must be saved to disk** after training — no in-memory only models.
8. **Bootstrap confidence intervals are required** for the RUL display on Page 4.
9. **The simulation must be stateful** — using `st.session_state` to persist cycle position.
10. **train_models.py must be runnable independently** of the Streamlit app.
