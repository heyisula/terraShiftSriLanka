<div align="center">

# 🌿 TerraShift Sri Lanka

### Satellite-Based Deforestation & Land-Cover Change Analysis
### Kalpitiya Peninsula, Sri Lanka · 2016 – 2025

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Rasterio](https://img.shields.io/badge/Rasterio-GIS-4B8BBE?style=for-the-badge&logo=qgis&logoColor=white)](https://rasterio.readthedocs.io)

[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=for-the-badge)](https://matplotlib.org)
[![Pandas](https://img.shields.io/badge/Pandas-Data-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![SciPy](https://img.shields.io/badge/SciPy-Statistics-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br/>

> **A fully reproducible, machine-learning-driven remote sensing pipeline** that tracks, classifies, and forecasts deforestation across the Kalpitiya coastal ecosystem using 10 years of Landsat satellite imagery.

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Study Area](#️-study-area)
- [Pipeline Architecture](#-pipeline-architecture)
- [Outputs & Visualisations](#-outputs--visualisations)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
- [Dependencies](#-dependencies)
- [Academic Context](#-academic-context)
- [License](#-license)

---

## 🌍 Overview

**TerraShift Sri Lanka** ingests raw **Landsat 8 & 9 Level-2 Surface Reflectance** imagery and produces publication-grade environmental analytics — all from a single self-contained Jupyter notebook (`retrain.ipynb`).

The pipeline handles every stage of a professional remote sensing workflow:

| Stage | What it does |
|-------|-------------|
| 🛰️ **Ingest** | Discovers and loads 10 multi-year Landsat scenes (2016 → 2025) |
| ☁️ **Cloud Mask** | Removes cloud-contaminated pixels using the QA-Pixel band |
| 🧮 **Feature Engineering** | Derives 11 spectral features: B2–B7, NDVI, NDWI, NDBI, NBR, EVI |
| 🗺️ **Land Masking** | Builds a persistent NDWI > 0.15 water mask + GPS-to-UTM ROI crop |
| 🤖 **Classification** | Trains dual Random Forest models (11-feature + 6-band baseline) |
| ✅ **Validation** | Cross-scene validation on 3 unseen dates → Accuracy + Cohen's κ |
| 📤 **Export** | Writes GIS-ready GeoTIFFs with **native embedded RGBA colormaps** |
| 🔄 **Change Detection** | Pixel-wise class transitions → loss/gain/net hectares per interval |
| 📈 **Forecasting** | Triple-model ensemble + 95% confidence interval projected to 2030 |

---

## 🛰️ Study Area

<div align="center">

| Property | Value |
|----------|-------|
| **Location** | Kalpitiya Peninsula, Northwest Sri Lanka |
| **Bounding Box** | Lat `8.00° – 8.65° N` · Lon `79.68° – 79.90° E` |
| **WRS-2 Path/Row** | `142 / 054` |
| **Satellite** | Landsat 8 (LC08) & Landsat 9 (LC09) · Collection 2 · Level-2 SR |
| **Temporal Coverage** | February 2016 → March 2025 · **10 scenes** |
| **Bands** | B2–B7 (Surface Reflectance) + QA-Pixel |
| **Native Resolution** | 30 m per pixel |

</div>

The Kalpitiya Peninsula is a unique coastal ecosystem under severe land-use pressure — shrimp aquaculture ponds, salt pans, mangrove clearance, and urban expansion all compete within a narrow strip of land. The pipeline isolates this ROI with a `pyproj` GPS-to-UTM coordinate transformation, then applies a bitwise AND with the persistent land mask to completely exclude the Indian Ocean and Puttalam Lagoon.

---

## 🔬 Pipeline Architecture

### 1 · Spectral Index Computation

Six indices are derived per scene and written to `out/ndvi/`, `out/ndwi/`, etc.:

```python
NDVI = (B5 - B4) / (B5 + B4)          # Vegetation health
NDWI = (B3 - B5) / (B3 + B5)          # Water / coastal inundation
NDBI = (B5 - B6) / (B5 + B6)          # Built-up / impervious surfaces
NBR  = (B5 - B7) / (B5 + B7)          # Burn scar / bare soil
EVI  = 2.5 * (B5-B4)/(B5+6*B4-7.5*B2+1)  # Enhanced canopy signal
```

### 2 · Persistent Land Mask + ROI Crop

```python
# Pixels that are water in >60% of scenes are flagged permanently
LAND_MASK = (ndwi_stack > 0.15).mean(axis=0) > 0.6

# GPS → projected CRS → raster pixel address
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
x_min, y_min = transformer.transform(79.68, 8.00)
x_max, y_max = transformer.transform(79.90, 8.65)
row_min, col_min = rowcol(transform, x_min, y_min)

KALP_MASK = LAND_MASK & ROI_MASK   # final mask: land pixels inside the peninsula only
```

### 3 · Dual Random Forest Classification

Two models are trained on pseudo-labels generated from the reference scene (earliest date):

```
Standard RF  →  11 features  (B2-B7 + NDVI + NDWI + NDBI + NBR + EVI)
Bands-only RF  →  6 features  (B2-B7 only) — honest generalisation baseline
```

Both are cross-validated on **3 completely unseen chronological scenes**, recording:

- `Accuracy` — fraction of correctly classified land pixels  
- `Cohen's κ` — chance-corrected agreement (Kappa ≥ 0.80 = *Excellent*)

### 4 · GIS-Ready Classification Export

Every classified scene is written as a **LZW-compressed GeoTIFF** with a native embedded RGBA colormap so it opens in the correct colors in QGIS / ArcGIS without any configuration:

```python
dst.write_colormap(1, {
    0: (33,  113, 181, 255),   # 💧 Water      → Blue
    1: (35,  139,  69, 255),   # 🌿 Vegetation → Green
    2: (212, 168,  67, 255),   # 🟡 Bare Soil  → Yellow
    3: (203,  24,  29, 255),   # 🔴 Built-Up   → Red
})
```

### 5 · Sequential Change Detection

For every consecutive scene pair the pipeline computes:

| Metric | Description |
|--------|-------------|
| `lost_ha` | Hectares of vegetation converted to another class |
| `gained_ha` | Hectares where vegetation recovered |
| `net_ha` | Net change (negative = net deforestation) |
| `loss_rate` | Annualised loss velocity (ha / year) |

Results are saved to `out/stats/sequential_changes.csv`.

### 6 · Ensemble Trend Forecasting to 2030

Three complementary models are fitted to the NDVI time-series:

```python
lin  = LinearRegression()                              # long-term slope
poly = make_pipeline(PolynomialFeatures(2), LR())      # acceleration curves
gbr  = GradientBoostingRegressor(n_estimators=100)     # step-wise changes

ensemble_forecast = (lin + poly + gbr) / 3             # arithmetic mean ensemble
```

A **95% confidence interval** is computed from residual standard error using the Student-t distribution:

```
CI_margin = t_crit × s_e × √(1/n + (x_future - x̄)² / SSx)
```

---

## 📊 Outputs & Visualisations

All figures are saved to `out/graphs/` at ≥ 130 dpi using a harmonious scientific colour palette.

| File | Description |
|------|-------------|
| `rfAccuracyEval.png` | 3-panel ML dashboard: Confusion Matrix · Cross-scene accuracy bars · Gini Feature Importances |
| `beforeVsAfter.png` | Side-by-side baseline (2016) vs. final (2025) classified spatial maps |
| `deforestrationRates.png` | Annualised deforestation vs. regrowth bar chart (ha/year per interval) |
| `landCoverTrend.png` | Stacked bar chart of all 4 land-cover classes across every scene |
| `summeryPred.png` | 4-panel summary: NDVI trend · dense vegetation % · stacked composition · hectare trajectories |
| `ndviImagesGrid.png` | 4-column multi-temporal NDVI spatial grid across all scenes |
| `ndviHistGraph.png` | Overlapping NDVI density distributions across all scenes |
| `presistentLandMark.png` | Persistent land mask visualisation (green = land, white = masked water) |

> All GeoTIFFs in `out/classmaps/` carry **embedded colour tables** — just open them in QGIS and they render correctly with no extra setup.

---

## 📁 Repository Structure

```
terraShiftSriLanka/
│
├── 📓 retrain.ipynb              ← MASTER PIPELINE (run this)
├── 🐍 catogirizingData.py        ← organises raw Landsat tarballs
├── 🐍 getFileNames.py            ← extracts scene filenames & metadata
├── 📄 README.md
├── 📄 LICENSE
├── ⚙️  .gitignore
│
├── data/
│   └── raw/                      ← Landsat scenes (git-ignored)
│       ├── 2016_02/
│       ├── 2016_03/
│       └── ...
│
└── out/                          ← All pipeline outputs
    ├── classmaps/                ← Classified GeoTIFFs (RGBA embedded)
    ├── change/                   ← Pairwise change-detection rasters
    ├── graphs/                   ← PNG visualisations (tracked in git)
    ├── models/                   ← rf_model.pkl · scaler.pkl · rf_bands_only.pkl
    ├── stats/                    ← CSV tables (tracked in git)
    ├── ndvi/ ndwi/ ndbi/         ← Spectral index rasters (git-ignored)
    ├── nbr/ evi/                 ← Additional index rasters (git-ignored)
    └── stacked/                  ← Multi-band stacked TIFFs (git-ignored)
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/heyisula/terraShiftSriLanka.git
cd terraShiftSriLanka
```

### 2. Install dependencies

```bash
pip install rasterio numpy pandas scikit-learn matplotlib seaborn \
            scipy joblib pyproj tqdm
```

### 3. Add raw Landsat scenes

Place USGS Level-2 scene folders under `data/raw/`:

```
data/raw/2016_02/LC08_L2SP_142054_20160203_XXXXXXXX_SR_B2.TIF
data/raw/2016_02/LC08_L2SP_142054_20160203_XXXXXXXX_SR_B3.TIF
...
data/raw/2025_03/LC09_L2SP_142054_20250307_XXXXXXXX_SR_B7.TIF
```

### 4. Run the pipeline

**Option A — Jupyter Notebook (recommended)**

```bash
jupyter notebook retrain.ipynb
# Click ▶▶ Run All Cells
```

**Option B — VS Code**

Open `retrain.ipynb` in VS Code and click **Run All** in the notebook toolbar.

All outputs will be written automatically to `out/`.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `rasterio` | GeoTIFF I/O, CRS handling, colormap embedding |
| `numpy` | Array math, masking, feature matrices |
| `pandas` | Tabular data, time-series, CSV export |
| `scikit-learn` | Random Forest, StandardScaler, metrics |
| `scipy` | Student-t CI, linear regression stats |
| `matplotlib` + `seaborn` | All visualisations and dashboards |
| `pyproj` | GPS WGS84 → UTM coordinate transformation |
| `joblib` | Model serialization (`pkl` files) |

---

## 🎓 Academic Context

This project was developed as a **final group project** for the *Image Processing & Environmental Management* module (`HNDCSAI 25.2`). It follows rigorous academic remote sensing practices:

- ✅ Cloud masking with QA-Pixel confidence thresholds  
- ✅ Persistent water mask to prevent ocean/lagoon contamination of statistics  
- ✅ Cross-scene validation on unseen temporal scenes (not just a train/test split)  
- ✅ Dual-model comparison to quantify the value of engineered spectral indices  
- ✅ Statistically grounded forecasting with Student-t confidence intervals  
- ✅ All outputs are publication-grade and directly insertable into a university report  

---

## 📄 License

Released under the **MIT License** — see [`LICENSE`](LICENSE) for details.

---

<div align="center">

Made with 🛰️ Python and remote sensing science · Kalpitiya Peninsula, Sri Lanka

**[⭐ Star this repo](https://github.com/heyisula/terraShiftSriLanka)** if it helped you!

</div>