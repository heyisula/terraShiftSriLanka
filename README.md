# 🌳 Kalpitiya Deforestation Analysis
### Satellite-Based Land Cover Change Detection — Sri Lanka (2016–2025)

---

## 📍 Study Area
- **Location:** Kalpitiya, Sri Lanka
- **Coordinates:** Lat 8.2369°N, Lon 79.7628°E
- **WRS-2 Path/Row:** 142/054

## 🛰️ Dataset
- **Source:** USGS Landsat Collection 2, Level-2 Surface Reflectance
- **Satellites:** Landsat 8 (LC08) & Landsat 9 (LC09)
- **Time Period:** February 2016 – March 2025 (10 scenes)
- **Bands Used:** B1–B7 (SR), QA_PIXEL (cloud mask)

---

## 🗂️ Repository Structure

```
kalpitiya-deforestation-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
│
├── data/
│   ├── raw/                    # Original Landsat scenes
│   │   ├── 2016_02/
│   │   ├── 2016_03/
│   │   ├── 2017_02/
│   │   ├── 2017_03/
│   │   ├── 2019_02/
│   │   ├── 2020_03/
│   │   ├── 2022_02/
│   │   └── 2025_03/
│   ├── processed/              # Preprocessed outputs
│   │   ├── stacked_bands/
│   │   ├── ndvi/
│   │   ├── ndwi/
│   │   └── ndbi/
│   └── outputs/                # Final analysis results
│       ├── classification_maps/
│       ├── change_detection/
│       ├── graphs/
│       └── statistics/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_feature_engineering_ndvi_ndbi_ndwi.ipynb
│   ├── 04_landcover_classification.ipynb
│   ├── 05_change_detection.ipynb
│   └── 06_trend_forecasting.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── indices.py
│   ├── classification.py
│   ├── change_detection.py
│   ├── visualization.py
│   └── utils.py
│
├── models/
│   ├── random_forest_model.pkl
│   └── scaler.pkl
│
├── reports/
│   ├── figures/
│   └── final_report.pdf
│
└── scripts/
    ├── run_pipeline.py
    └── batch_process.py
```

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/kalpitiya-deforestation-analysis.git
cd kalpitiya-deforestation-analysis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Place Landsat Data
```
data/raw/2016_02/  ← LC08_L2SP_142054_20160203_*_SR_B*.TIF
data/raw/2016_03/  ← LC08_L2SP_142054_20160306_*_SR_B*.TIF
...
data/raw/2025_03/  ← LC09_L2SP_142054_20250307_*_SR_B*.TIF
```

### 4. Run Notebooks (in order)
```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

### 5. Or Run Full Pipeline
```bash
python scripts/run_pipeline.py
```

---

## 📊 Analysis Pipeline

| Step | Notebook | Description |
|------|----------|-------------|
| 1 | `01_data_exploration.ipynb` | Load scenes, inspect metadata, preview bands |
| 2 | `02_preprocessing.ipynb` | Cloud masking, band stacking, normalization |
| 3 | `03_feature_engineering.ipynb` | NDVI, NDWI, NDBI computation |
| 4 | `04_landcover_classification.ipynb` | Random Forest land cover classification |
| 5 | `05_change_detection.ipynb` | Multi-temporal change detection |
| 6 | `06_trend_forecasting.ipynb` | NDVI time-series & ML forecasting |

---

## 🛠️ Technologies
- **Python 3.9+**
- **rasterio** — Raster I/O and spatial operations
- **numpy / scipy** — Numerical computation
- **scikit-learn** — Machine learning (Random Forest)
- **matplotlib / seaborn** — Visualization
- **geopandas** — Geospatial vector operations
- **pandas** — Data management

---

## 📝 Key Results
- Vegetation cover change between 2016 and 2025
- NDVI trend analysis with ML forecasting
- Land cover classification maps (vegetation, water, bare soil, built-up)
- Change detection heatmaps

---

## 👨‍🎓 Academic Context
University-level remote sensing group project.
Study area: Kalpitiya Peninsula, Sri Lanka — a unique coastal ecosystem subject to land-use pressure.

---

## 📄 License
MIT License — see [LICENSE](LICENSE)
