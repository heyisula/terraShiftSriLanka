# 🌍 TerraShift Sri Lanka: Kalpitiya Deforestation Analysis

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)]()
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626.svg?style=for-the-badge&logo=Jupyter&logoColor=white)]()
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)]()
[![Rasterio](https://img.shields.io/badge/Rasterio-GIS-green.svg?style=for-the-badge)]()
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Data_Viz-blueviolet.svg?style=for-the-badge)]()
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)]()

---

## 📖 Project Overview
**TerraShift Sri Lanka** is a comprehensive, machine-learning-powered remote sensing pipeline designed to track, quantify, and forecast deforestation and land cover changes in the **Kalpitiya Peninsula** of Northwest Sri Lanka. Built as a high-end university research project for Image Processing and Environmental Management, this pipeline ingests raw Landsat satellite imagery and outputs publication-grade scientific analytics.

By utilizing **Multi-temporal Random Forest Classification** and **Statistical Ensemble Forecasting**, this project isolates human-driven environmental changes (such as shrimp aquaculture expansion and urbanization) from natural coastal dynamics.

---

## 🛰️ Study Area: Kalpitiya Peninsula
- **Coordinates:** Lat `8.00°`–`8.65°N`, Lon `79.68°`–`79.90°E`
- **Ecosystem:** Coastal mangroves, shrimp aquaculture, salt pans, and scrub forests.
- **Geospatial Masking:** The pipeline applies a dynamic WGS84 GPS-to-UTM projection (`pyproj`) bounding box mask, combined with a persistent water mask, to completely isolate terrestrial vegetation from the surrounding Indian Ocean and Puttalam Lagoon so statistics are not skewed by tidal anomalies.

---

## 🔬 Core Methodology & Pipeline Architecture

### 1. Advanced Feature Engineering
We compute a robust 11-feature structural matrix from Landsat Level-2 Surface Reflectance (Bands 2-7):
- **NDVI** (Normalized Difference Vegetation Index) - Tracks canopy health.
- **NDWI** (Normalized Difference Water Index) - Flags coastal inundation and salt pans.
- **NDBI** (Normalized Difference Built-up Index) - Detects urban sprawl.
- **NBR** (Normalized Burn Ratio) & **EVI** (Enhanced Vegetation Index).

### 2. Dual Random Forest Machine Learning Classification
To ensure scientific integrity, the pipeline trains and cross-validates two models side-by-side:
- **Standard Model (11 Features):** Uses raw bands + engineered spectral indices.
- **Baseline Model (6 Features):** Uses only raw spectral bands to prove index efficacy.
- **Cross-Scene Generalization:** Models are trained on a baseline year and evaluated on **completely unseen chronological scenes** to ensure true generalization across different atmospheric conditions over the decade.

### 3. Statistical Trend Forecasting (to 2030)
We built a **Triple-Model Forecasting Ensemble** to project deforestation trajectories:
- **Linear Regression:** Captures the long-term uniform trajectory.
- **Quadratic Polynomial Pipeline:** Captures historical acceleration curves.
- **Gradient Boosting Regressor:** Captures tight, complex historical step shifts.
- **Uncertainty Math:** Incorporates Student's t-distribution residual calculations to plot a rigorous **95% Confidence Interval envelope**.

---

## 📁 Repository Structure
The workspace is cleanly unified under a single master pipeline notebook:

```text
terraShiftSriLanka/
├── retrain.ipynb          # THE MASTER PIPELINE: End-to-end ML, GIS, and visualization notebook
├── catogirizingData.py    # Automation script to organize raw Landsat tarballs
├── getFileNames.py        # Automation script to extract metadata
├── data/                  # Raw Landsat Collection 2 GeoTIFFs (Ignored in Git)
└── out/                   # High-value analytical outputs
    ├── change/            # Spatial forest clearing/hotspot maps
    ├── classmaps/         # QGIS-ready classified GeoTIFFs with native RGBA colormaps
    ├── graphs/            # Publication-grade charts and dashboards (Tracked)
    ├── models/            # Serialized joblib Random Forest weights (Tracked)
    └── stats/             # Sequential change detection spreadsheets (Tracked)
```

---

## 📊 High-End Visual Analytics
All outputs are generated in `out/graphs/` with premium matplotlib styling:
1. **The 3-Panel ML Diagnostics Dashboard:** Features a Seaborn Confusion Matrix, cross-scene grouped bar accuracy validation, and Gini Feature Importance plots.
2. **The 4-Plot Statistical Summary Dashboard:** Contains Savitzky-Golay smoothed NDVI trends, stacked land composition histories, and continuous hectare trajectories over time.
3. **Annualized Deforestation Rates Bar Chart:** Analyzes the exact speed of forest clearing (Hectares / Year) with self-contained decimal year math.
4. **Before vs. After GIS Mapping:** High-resolution side-by-side spatial maps comparing baseline to final years with custom legends.

---

## 🚀 How to Run the Pipeline

1. **Clone the repository:**
   ```bash
   git clone https://github.com/heyisula/terraShiftSriLanka.git
   cd terraShiftSriLanka
   ```

2. **Install dependencies:**
   ```bash
   pip install rasterio numpy pandas scikit-learn matplotlib seaborn pyproj scipy joblib
   ```

3. **Execute the Master Notebook:**
   Open `retrain.ipynb` in VS Code or Jupyter, and click **"Run All"**. 
   *Note: The notebook is 100% self-contained, completely immune to cell-ordering dependency bugs, and compiles with zero syntax errors.*

---

## 🎓 Academic Context
This repository represents a final university group project for Image Processing. The codebase adheres to strict academic remote sensing standards, utilizing proper bitwise masking, temporal compositing, cross-scene validation, and statistically sound predictive forecasting.

<div align="center">
  <i>Developed with Python, Science, and precision.</i>
</div>
