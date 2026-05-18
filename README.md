# 🌍 TerraShift Sri Lanka: Kalpitiya Deforestation & Land‑Cover Change Analysis  
*Satellite‑based remote sensing of the Kalpitiya Peninsula, Sri Lanka (2016‑2025)*  

---  

## Badges  

|  |  |
|---|---|
| ![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.10-blue?logo=python&logoColor=white) | ![Jupyter](https://img.shields.io/badge/Jupyter‑Notebook-F37626?logo=jupyter&logoColor=white) |
| ![Rasterio](https://img.shields.io/badge/Rasterio-1.3%2B-4B8BBE?logo=github) | ![scikit‑learn](https://img.shields.io/badge/scikit‑learn-1.5%2B-F7931E?logo=scikit-learn) |
| ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?logo=matplotlib) | ![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?logo=pandas) |
| ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg) | ![OS: Windows](https://img.shields.io/badge/OS-Windows-0078D6?logo=windows) |

---  

## 📖 Project Overview  

**TerraShift Sri Lanka** is a fully reproducible, machine‑learning‑driven pipeline that:

* **Ingests** Level‑2 Landsat 8/9 surface‑reflectance scenes (10 dates from 2016 → 2025).  
* **Masks** clouds, permanent water, and ocean, then isolates the **Kalpitiya peninsula** with a GPS‑to‑UTM ROI.  
* **Derives** 11 spectral features (6 raw bands + NDVI, NDWI, NDBI, NBR, EVI).  
* **Trains** two Random‑Forest classifiers:  
  * **Standard model** – all 11 features.  
  * **Bands‑only model** – raw 6 bands (baseline).  
* **Validates** on three out‑of‑sample scenes (cross‑scene accuracy, Cohen’s κ).  
* **Classifies** every scene, writes GIS‑ready GeoTIFFs with **embedded RGBA colormaps** (forest‑green, soil‑yellow, built‑up‑red, water‑blue).  
* **Computes** pixel‑wise loss/gain/net hectares for each consecutive pair of scenes.  
* **Builds** an NDVI time‑series, fits three complementary models (linear, quadratic polynomial, Gradient‑Boosting), ensembles them, and draws a **95 % confidence interval** using Student‑t residual analysis.  

All results are saved under `out/` as **publication‑grade PNGs** and CSV tables ready for a university report.

---  

## 🛰️ Study Area & Data Sources  

| Item | Details |
|------|---------|
| **Location** | Kalpitiya Peninsula, Northwest Sri Lanka (≈ 8.00° – 8.65° N, 79.68° – 79.90° E). |
| **Satellite** | USGS **Landsat 8 (LC08)** & **Landsat 9 (LC09)** – Collection‑2 Level‑2 Surface Reflectance. |
| **Temporal coverage** | Feb 2016 → Mar 2025 (10 cloud‑free scenes). |
| **Bands used** | B2–B7 (SR) + QA‑Pixel (cloud mask). |
| **Indices derived** | NDVI, NDWI, NDBI, NBR, EVI. |
| **Reference mask** | Persistent NDWI > 0.15 mask applied to all scenes; ROI extracted via `pyproj` transformation. |

Raw scenes belong in `data/raw/<YYYY_MM>/` (the folder is ignored in Git).

---  

## 🔬 Core Methodology  

### 1. Data Ingestion & Cloud Masking  

```python
SCENES = discover_scenes(RAW_DIR)   # auto‑detect all *_stack.tif files
with rasterio.open(stk_path) as src:
    stack = src.read().astype(np.float32)          # 7‑band stack
    qa    = read_qa_pixel(stk_path)               # cloud mask
    stack = apply_cloud_mask(stack, qa)            # keep only clear pixels
```

### 2. Feature Engineering  

```python
ndvi = (B5 - B4) / (B5 + B4)
ndwi = (B3 - B5) / (B3 + B5)
ndbi = (B5 - B6) / (B5 + B6)
nbr  = (B5 - B7) / (B5 + B7)
evi  = 2.5 * (B5 - B4) / (B5 + 6*B4 - 7.5*B2 + 1)

X_std   = np.column_stack([B2,B3,B4,B5,B6,B7,ndvi,ndwi,ndbi,nbr,evi])
X_bands = np.column_stack([B2,B3,B4,B5,B6,B7])
```

All features are flattened to a 2‑D matrix and masked by `vmask` (valid pixel mask).

### 3. Land‑Mask & ROI Extraction  

```python
# Persistent water mask (NDWI > 0.15 in >60 % of scenes)
LAND_MASK = (NDWI > 0.15)

# GPS → UTM conversion for the ROI polygon
transform = pyproj.Transformer.from_crs("EPSG:4326", crs, always_xy=True)
x_min, y_min = transform.transform(lon_min, lat_min)
x_max, y_max = transform.transform(lon_max, lat_max)

# Convert projected coordinates → raster row/col
row_min, col_min = rasterio.transform.rowcol(land_transform, x_min, y_min)
row_max, col_max = rasterio.transform.rowcol(land_transform, x_max, y_max)

ROI_MASK = np.zeros_like(LAND_MASK, dtype=bool)
ROI_MASK[row_min:row_max+1, col_min:col_max+1] = True
KALP_MASK = LAND_MASK & ROI_MASK
```

### 4. Training & Cross‑Scene Validation  

*Pseudo‑labels* are generated from NDVI/NDWI/NDBI thresholds, then two Random‑Forest models are trained:

```python
RF   = RandomForestClassifier(n_estimators=300, random_state=42)
RF_B = RandomForestClassifier(n_estimators=300, random_state=42)

RF.fit(X_std_sc, y_labelled)
RF_B.fit(X_bands_sc, y_labelled)
```

Validation on `val_labels = [LABELS[4], LABELS[9], LABELS[14]]` records **accuracy** and **Cohen’s κ** for both models.

### 5. Classification & GIS‑Ready Export  

```python
preds = RF.predict(X_sc).astype(np.int8)
cmap  = np.full((H, W), -1, dtype=np.int8)   # -1 = nodata (masked ocean)
cmap[vmask] = preds
cmap[~KALP_MASK] = -1

profile.update(count=1, dtype="int8", nodata=-1, compress="lzw")
with rasterio.open(out_path, "w", **profile) as dst:
    dst.write(cmap[np.newaxis, :, :])
    dst.write_colormap(1, {
        0: (33, 113, 181, 255),   # Water – blue
        1: (35, 139, 69, 255),    # Vegetation – green
        2: (212, 168, 67, 255),   # Bare soil – yellow
        3: (203, 24, 29, 255)     # Built‑up – red
    })
```

### 6. Change Detection  

For every consecutive pair (`from → to`) the script counts class transitions, converts pixel counts to hectares, and stores the results in `out/stats/sequential_changes.csv`. The annualised loss/gain rates are visualised in `deforestrationRates.png`.

### 7. Trend Forecasting  

```python
# Linear model
lin   = LinearRegression().fit(X, y)

# Quadratic polynomial pipeline
poly  = make_pipeline(PolynomialFeatures(2), LinearRegression()).fit(X, y)

# Gradient‑Boosting Regressor
gbr   = GradientBoostingRegressor(n_estimators=100, random_state=42).fit(X, y)

# Ensemble forecast
ensemble = (lin.predict(X_f) + poly.predict(X_f) + gbr.predict(X_f)) / 3
```

A 95 % CI envelope is built using residual standard error `s_e` and Student’s‑t critical value `t_crit`. The final 4‑panel dashboard (`summeryPred.png`) shows the raw NDVI series, smoothed Savitzky‑Golay curve, ensemble forecast, and confidence interval.

---  

## 📁 Repository Structure  

```
terraShiftSriLanka/
├─ .gitignore               # ignores raw data, keeps only processed outputs
├─ LICENSE
├─ README.md                # <-- you are reading it!
├─ requirements.txt
│
├─ data/
│   └─ raw/                 # Landsat Collection‑2 scenes (git‑ignored)
│
├─ out/
│   ├─ classmaps/           # GIS‑ready classified GeoTIFFs (RGBA)
│   ├─ change/              # Pairwise change‑detection rasters
│   ├─ graphs/              # Publication‑grade PNG visualisations
│   ├─ models/              # Serialized RF models & scalers (joblib)
│   └─ stats/               # CSV tables (time‑series, change stats, forecast)
│
├─ notebooks/
│   └─ retrain.ipynb        # **MASTER PIPELINE** – end‑to‑end workflow
│
├─ src/
│   ├─ data_loader.py
│   ├─ preprocessing.py
│   ├─ indices.py
│   ├─ classification.py
│   ├─ change_detection.py
│   ├─ visualization.py
│   └─ utils.py
│
└─ scripts/
    ├─ run_pipeline.py      # CLI wrapper to execute `retrain.ipynb`
    └─ batch_process.py    # Optional bulk‑processing helper
```

---  

## 🚀 Installation & Usage  

1. **Clone the repository**  

```bash
git clone https://github.com/heyisula/terraShiftSriLanka.git
cd terraShiftSriLanka
```

2. **Create a virtual environment & install dependencies**  

```bash
python -m venv .venv
.\.venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
```

3. **Place the raw Landsat scenes**  

```
data/raw/2016_02/LC08_..._SR_B2.TIF
data/raw/2016_03/...
...
```

4. **Run the pipeline**  

*Option A – Jupyter*  

```bash
jupyter notebook notebooks/retrain.ipynb
# Click “Run All”
```

*Option B – CLI*  

```bash
python scripts/run_pipeline.py
```

All results appear under `out/`. Open any PNG in the `graphs/` folder for a ready‑to‑publish figure, or load a GeoTIFF from `classmaps/` in QGIS/ArcGIS (the embedded colormap renders automatically).

---  

## 📊 High‑End Visualisations (available in `out/graphs/`)  

| Figure | What it shows |
|--------|---------------|
| **04_rf_evaluation.png** | Confusion matrix, cross‑scene accuracy bar chart, feature‑importance plot (Standard RF). |
| **05_before_after_maps.png** | Side‑by‑side baseline vs. final classified maps (with custom legend). |
| **07_deforestation_rates.png** | Annual loss / gain (ha / yr) for every interval. |
| **06_summary_dashboard.png** | 4‑panel dashboard: NDVI trend, dense‑vegetation %, stacked land‑cover, hectare trajectories. |
| **summeryPred.png** | Ensemble NDVI forecast → 2030 with 95 % confidence envelope. |

All plots use a harmonious colour palette (forest‑green, soil‑yellow, built‑up‑red, water‑blue) and are saved at ≥ 300 dpi for publication quality.

---  

## 📚 Academic Context  

This repository was produced as the **final group project** for the *Image Processing & Environmental Management* module (HNDCSAI 25.2). The work meets university‑level remote‑sensing standards:  

* Proper handling of cloud masks and permanent water masks.  
* Cross‑scene validation to avoid over‑fitting.  
* Statistically rigorous forecasting with confidence intervals.  
* All outputs are fully reproducible and can be directly inserted into the project report.

---  

## 📄 License & Citation  

The code is released under the **MIT License** (see `LICENSE`).  

If you use this repository in a publication or academic work, please cite:

```bibtex
@misc{heyisula2026,
  author       = {Isula Dissanayake},
  title        = {TerraShift Sri Lanka: Kalpitiya Deforestation and Land‑Cover Change Analysis (2016‑2025)},
  year         = {2026},
  howpublished = {\url{https://github.com/heyisula/terraShiftSriLanka}},
  note         = {GitHub repository}
}
```

---  

## 🙏 Acknowledgements  

* **USGS EarthExplorer** – for the Landsat Collection‑2 Level‑2 SR data.  
* **NASA EOSDIS** – for the Landsat archive infrastructure.  
* The open‑source Python ecosystem (`rasterio`, `scikit‑learn`, `matplotlib`, `geopandas`, etc.).  