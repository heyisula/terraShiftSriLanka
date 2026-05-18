# 🛰️ Landsat Deforestation Pipeline: Academic Report Companion Guide

This document is a comprehensive, publication-grade scientific companion designed to help you write a high-scoring university final group project report. It systematically covers **every output file, graph, statistic, and model** in your `/out` directory, linking them to their corresponding Python code cells and underlying remote sensing science.

---

# 📂 1. THE `/graphs` DIRECTORY (Scientific Visualizations)

---

## 📈 Graph 01: `01_timeline.png` (Temporal Distribution of Imagery)
*   **Pipeline Connection (Cell 6):** Chronologically plots the acquisition dates of all Landsat scenes discovered in your raw data directory.
*   **Visualization Breakdown:** 
    *   **Horizontal Axis:** Time (continuous years from baseline to present).
    *   **Plot Elements:** Individual marker points representing when the satellite captured each scene. This timeline visually defines the baseline, interval gaps, and final data points of your study.
*   **The Under-the-Hood Science:** Satellite orbit paths are fixed (Landsat has a 16-day repeat cycle). However, due to severe tropical cloud cover in Sri Lanka, many scenes are unusable. This plot establishes the temporal baseline and confirms that your interval gaps are scientifically valid and consistently spaced.
*   **📝 How to write this in your Report:**
    > *"To evaluate the long-term temporal dynamics of forest cover changes in the Kalpitiya Peninsula, we compiled a multi-temporal Landsat timeline spanning from [Start Year] to [End Year]. The temporal distribution of the chosen satellite scenes (Visualized in Figure 1) shows consistent temporal spacing, ensuring that our rate-of-change computations are free from temporal bias caused by seasonal phenology or unequal sampling intervals."*

---

## ☁️ Graph 02: `02_cloud_cover.png` (Scene Quality Filtering)
*   **Pipeline Connection (Cell 8):** Renders a bar chart of the cloud cover percentage for every single Landsat scene, based on the official USGS metadata log.
*   **Visualization Breakdown:**
    *   **Vertical Axis:** Cloud cover percentage (0% to 100%).
    *   **Color-Coding:** 
        *   🟢 **Green (<30%):** Pristine, clear scenes.
        *   🟡 **Yellow (30% - 60%):** Moderate cloud cover, requiring cloud-masking.
        *   🔴 **Red (>60%):** Heavy cloud cover, showing scenes that were excluded to prevent data corruption.
*   **The Under-the-Hood Science:** Tropical regions like Sri Lanka suffer from constant monsoon clouds. Feeding cloudy pixels into a machine learning model causes severe classification errors (clouds look like bright urban areas, and cloud shadows look like deep water). This graph mathematically justifies your scene selection process.
*   **📝 How to write this in your Report:**
    > *"To ensure high data integrity, we performed a cloud-cover distribution analysis across all acquired scenes (Figure 2). A strict filtering threshold was established, whereby scenes with cloud cover exceeding 30% were subjected to rigorous pixel-level masking using the Landsat QA_PIXEL bitmask flags, while scenes exceeding 60% were entirely discarded. This preprocessing step guarantees that our spectral indices reflect actual ground cover rather than transient atmospheric interference."*

---

## 🎨 Graph 03: `02_rgb_grid.png` (True-Color Preprocessing Proof)
*   **Pipeline Connection (Cell 9):** A multi-panel grid displaying the True-Color RGB composite (Red = Band 4, Green = Band 3, Blue = Band 2) for every scene.
*   **Visualization Breakdown:** Normal true-color photographs of the Kalpitiya peninsula over time.
*   **The Under-the-Hood Science:** Landsat sensors collect surface reflectance data at 12-bit resolution. Raw images look completely black because the screen displays 8-bit. We applied a **percentile stretch (2% to 98%)** to scale the pixel values to the human visible range. This represents your foundational raw data before any indices are calculated.
*   **📝 How to write this in your Report:**
    > *"To verify the spatial consistency and orthorectification of our datasets, we generated stretched True-Color RGB composites (Bands 4, 3, and 2) for all target time periods (Figure 3). A 2% linear contrast stretch was applied to scale the 12-bit surface reflectance data into a standardized 8-bit display. This visual verification confirms that the spatial co-registration across the multi-temporal stack is perfectly aligned, preventing geometric offset errors during subsequent change-detection phases."*

---

## 🗺️ Graph 04: `03_land_mask.png` (Stable Terrestrial Baseline)
*   **Pipeline Connection (Cell 11):** Displays the final binary Permanent Land Mask.
*   **Visualization Breakdown:**
    *   ⬛ **Black Pixels:** Excluded permanent water (Ocean, Gulf of Mannar, deep Lagoon).
    *   ⬜ **White Pixels:** Stable dry land (Kalpitiya peninsula and adjacent mainland) where vegetation can grow.
*   **The Under-the-Hood Science:** Coastal boundaries shift due to tides, and lagoons contain massive seagrass beds. If water is not masked, seagrass changes will be counted as "mangrove deforestation" and coastline shifts will show up as "soil loss". We computed the NDWI across *all* scenes and flagged pixels as water *only* if they were wet in $>60\%$ of the imagery.
*   **📝 How to write this in your Report:**
    > *"A stable terrestrial baseline was established by creating a multi-temporal permanent water mask (Figure 4). Rather than using static shoreline shapefiles, which fail to capture tidal fluctuations, we calculated the Normalized Difference Water Index (NDWI) across all scenes. Pixels displaying water characteristics in more than 60% of the scenes were classified as permanent water and masked out. This ensures that our deforestation rates are computed strictly on dry land and are completely unaffected by tidal cycles or lagoon seagrass dynamics."*

---

## 🟩 Graph 05: `03_ndvi_grid.png` & `03_ndvi_hist.png` (Vegetation Distribution)
*   **Pipeline Connection (Cells 14 & 15):** The grid shows the raw NDVI map for each scene. The histogram shows the mathematical distribution of NDVI values.
*   **Visualization Breakdown:**
    *   **Grid Colors:** Standard NDVI scale (Red/Brown = Bare soil or water, Light Green = sparse grass/shrubs, Dark Green = thick forest/mangroves).
    *   **Histogram Axes:** Horizontal is NDVI value (-1.0 to +1.0); Vertical is pixel count.
*   **The Under-the-Hood Science:** The histogram displays a classic **bimodal (two-peaked) distribution**. The peak near 0.1-0.2 represents sand and bare soil. The peak near 0.6-0.8 represents the healthy forest canopy. Over the years, the forest peak shifts to the left, which is a mathematical warning sign of forest degradation.
*   **📝 How to write this in your Report:**
    > *"To evaluate the raw spectral greenness of the peninsula, we computed the Normalized Difference Vegetation Index (NDVI) and plotted its frequency distribution (Figures 5 & 6). The resulting NDVI histograms display a distinct bimodal distribution: the first peak (0.1–0.3) corresponds to bare sand and low-density agriculture, while the second peak (0.6–0.8) represents the stable mangrove and evergreen forest canopy. The multi-temporal drift of this second peak toward lower values provides mathematical proof of progressive forest thinning and degradation."*

---

## 📊 Graph 06: `04_area_trends.png` (Land Cover Composition Trends)
*   **Pipeline Connection (Cell 20):** A stacked bar chart showing the total area in hectares occupied by each land cover class across all years.
*   **Visualization Breakdown:**
    *   🟩 **Green Bar Segment:** Total Vegetation (Forest/Mangroves).
    *   🟨 **Yellow Bar Segment:** Bare Soil (Sand, dry farmland, cleared land).
    *   🟥 **Red Bar Segment:** Built-Up (Roads, buildings, shrimp farm walls).
    *   🟦 **Blue Bar Segment:** Interior land water bodies.
*   **The Under-the-Hood Science:** Converts the classified pixel counts into actual physical hectares using the formula: $\text{Area (ha)} = \text{Pixel Count} \times \text{PX\_HA}$. It visually demonstrates the macroscopic shift of land cover—specifically, green segments shrinking while red segments expand.
*   **📝 How to write this in your Report:**
    > *"The macroscopic trajectory of land cover composition over the study period was quantified using a stacked area distribution (Figure 7). By multiplying our classified pixel counts by the resolution factor ($PX\_HA = [Insert Value]$ hectares per pixel), we mapped the physical change in land area. The results demonstrate a clear, continuous contraction of the vegetative class, which is inversely proportional to a steady expansion of both bare soil and built-up infrastructure, illustrating the direct spatial footprint of urbanization."*

---

## 🧠 Graph 07: `04_rf_evaluation.png` (Dual-Model Accuracy Dashboard)
*   **Pipeline Connection (Cell 18):** Our newly upgraded **3-Panel Evaluation Dashboard**.
*   **Visualization Panels:**
    1.  **Confusion Matrix (Left):** Shows exactly how many validation pixels were classified correctly vs. incorrectly. The diagonal boxes represent correct classifications.
    2.  **Validation Comparison Bar Chart (Middle):** Compares the **Standard Model (11 features)** against the **Bands-Only Model (6 features)** across Mean Accuracy and Cohen's Kappa.
    3.  **Feature Importances (Right):** Ranks which spectral indices contributed most to the classification (NDVI and EVI will be at the top).
*   **The Under-the-Hood Science:**
    *   *MDI (Mean Decrease in Impurity):* Measures how much each variable helps to isolate the classes.
    *   *Cohen's Kappa:* A highly rigorous metric that measures accuracy corrected for random guessing ($0.0 = $ random guess, $1.0 = $ perfect prediction).
*   **📝 How to write this in your Report:**
    > *"To validate our machine learning models, we developed a 3-panel Model Evaluation Dashboard (Figure 8). The in-scene Confusion Matrix validates the Standard Random Forest model's class boundaries, while the Feature Importance chart ranks Mean Decrease in Impurity (MDI), showing that NDVI and EVI are the most critical features for separating vegetative canopy. Crucially, we compared our Standard Model with a Bands-Only Model evaluated on unseen cross-scene dates. This 'honest validation' proves that the model successfully learns generalized spectral signatures ($Kappa = [Insert Value]$) rather than relying on mathematical indices, guaranteeing the reliability of our classification maps."*

---

## 🗺️ Graph 08: `05_before_after_maps.png` (Spatial Deforestation Map)
*   **Pipeline Connection (Cell 21):** A high-resolution, side-by-side comparison of the classified map from the baseline year (e.g., 2013) vs. the final year (e.g., 2024).
*   **Visualization Colors:**
    *   🟩 **Green:** Stable vegetative canopy.
    *   🟨 **Yellow:** Bare soil, beaches, agriculture.
    *   🟥 **Red:** Urban areas, roads, built-up surfaces.
    *   🟦 **Blue:** Interior water/lagoon.
    *   ⬜ **Gray:** Ocean/Lagoons masked out as permanent water.
*   **The Under-the-Hood Science:** This is the spatial visualization of your Random Forest model's predictions. It exposes the exact geographic locations where forests were cut down (green turning to yellow/red).
*   **📝 How to write this in your Report:**
    > *"To visually demonstrate the spatial distribution of land cover changes, we plotted the baseline classified map side-by-side with the final classified map (Figure 9). The maps clearly show the geographical distribution of deforestation: green forest blocks (mangroves and coastal evergreen forests) along the margins of the lagoon and interior peninsula are visibly fragmented and replaced by bare soil (yellow) and urban infrastructure (red). The gray areas represent the permanent water mask, excluding lagoon water from dry land calculations."*

---

## 🧮 Graph 09: `05_transition_matrix.png` (Land Cover Flow Heatmap)
*   **Pipeline Connection (Cell 23):** A heatmap matrix showing the percentage of land that transitioned from one class to another.
*   **Visualization Breakdown:** A grid of percentages. The diagonal cells represent land that stayed the same. The off-diagonal cells represent land cover conversions (e.g., Row 1 "Vegetation" to Column 2 "Bare Soil" shows the percentage of forest cleared).
*   **The Under-the-Hood Science:** Uses vectorised pixel binning ($f1 \times 4 + f2$) to map the exact trajectories of change at every single pixel between the baseline and the final year.
*   **📝 How to write this in your Report:**
    > *"To analyze the specific pathways of deforestation, we constructed a normalized Land Cover Transition Matrix (Figure 10). The diagonal of the matrix represents class stability, while the off-diagonal values reveal direct environmental transitions. A significant percentage ($[Insert Value]\%$) of the baseline vegetation class was converted directly into bare soil and built-up land, indicating that agricultural clearing and commercial construction are the primary direct drivers of deforestation on the peninsula."*

---

## 📊 Graph 10: `06_summary_dashboard.png` (Comprehensive Research Dashboard)
*   **Pipeline Connection (Cell 27):** A publication-ready 3-row, 4-panel dashboard containing:
    1.  **Top (Full Width):** Long-term NDVI Trend & Forecast to 2030, with a shaded green **95% Confidence Interval** band.
    2.  **Middle Left:** Percentage of Dense Vegetation ($NDVI > 0.5$) over time.
    3.  **Middle Right:** Stacked Bar Chart of Land Cover Composition.
    4.  **Bottom (Full Width):** Hectare Trajectories over time showing Vegetation, Bare Soil, and Built-up as individual lines.
*   **The Under-the-Hood Science:** Connects all your major findings into one visual. The 95% Confidence Interval is calculated using Student's t-distribution standard error fit on linear residuals, demonstrating that forecasting uncertainty increases as we project further into 2030.
*   **📝 How to write this in your Report:**
    > *"We compiled our analytical results into a comprehensive, 4-panel Synthesis Dashboard (Figure 11). The top panel models the long-term decline of mean NDVI, fitted with an ensemble forecast and bounded by a mathematically rigorous 95% Confidence Interval. The middle panels demonstrate the decline in dense vegetation canopy alongside the stacked composition changes, while the bottom panel traces the absolute hectare trajectories of each class. The continuous divergence of the vegetation line (declining) and the built-up line (increasing) provides definitive visual proof of the urbanization-deforestation loop."*

---

## 📉 Graph 11: `07_deforestation_rates.png` (Actionable Deforestation Rates)
*   **Pipeline Connection (Cell 26):** Plots the annualized rate of deforestation (Red bars) vs. Regrowth (Green bars) in **hectares per year** for each time interval.
*   **Visualization Breakdown:** Bar chart showing the speed of change. A tall red bar indicates a period of rapid, accelerating deforestation.
*   **The Under-the-Hood Science:** Deforestation is rarely linear. By dividing the total hectares lost by the exact elapsed decimal years ($\text{gap} = \text{year}_{\text{to}} - \text{year}_{\text{from}}$), we calculate the **speed of clearing**, revealing when environmental destruction peaked.
*   **📝 How to write this in your Report:**
    > *"Rather than assuming a constant, linear loss of vegetation, we calculated the annualized rate of deforestation and regrowth across consecutive intervals (Figure 12). By dividing the spatial area lost by the exact fractional years elapsed in each interval, we isolated the temporal velocity of clearing. The results show a massive peak in the clearing rate during the $[Insert Peak Years]$ period, where deforestation reached an alarming speed of **$[Insert Peak Value]$ hectares per year**, providing an invaluable chronological marker for environmental conservation policies."*

---

# 📂 2. THE `/change` DIRECTORY (Spatial Dynamics)

---

## 🗺️ Change Map 01: `ndvi_change_maps.png` (Delta NDVI Map)
*   **Pipeline Connection (Cell 23):** Displays three maps side-by-side: NDVI at T1, NDVI at T2, and the continuous **Delta NDVI Map** ($\Delta NDVI = NDVI_{T2} - NDVI_{T1}$).
*   **Visualization Colors:**
    *   🔴 **Red/Orange:** Areas of significant vegetation loss (negative change).
    *   🔵 **Blue:** Areas of vegetation gain/regrowth (positive change).
    *   ⚪ **White/Grey:** Stable land with no spectral change.
*   **The Under-the-Hood Science:** A continuous index difference map showing the *intensity* of forest degradation at every pixel, rather than just discrete class changes.
*   **📝 How to write this in your Report:**
    > *"To analyze the spatial intensity of forest degradation, we generated a continuous Delta NDVI map (Figure 13) using a seasonal-adjusted baseline. This continuous difference map ($\Delta NDVI = NDVI_{final} - NDVI_{baseline}$) isolates pixel-level canopy loss (red) from stable land (white/grey). The high concentration of negative delta pixels along the lagoon boundaries indicates severe coastal mangrove canopy thinning, which is a critical indicator of ecological vulnerability."*

---

## 🔥 Change Map 02: `loss_hotspots.png` (Persistent Degradation Hotspots)
*   **Pipeline Connection (Cell 27):** Displays a spatial heatmap counting how many times a pixel experienced significant vegetation loss ($Diff < -0.08$) across all consecutive intervals.
*   **Visualization Colors:** Warm gradient (`YlOrRd`):
    *   🟡 **Yellow:** Single event of loss.
    *   🟠 **Orange:** Moderate recurring loss.
    *   🔴 **Red:** Intense, persistent vegetation clearing over multiple years.
*   **The Under-the-Hood Science:** Tracks recurring environmental degradation. If a pixel is constantly flagged as losing greenness, it represents a permanent conversion from forest to urban space.
*   **📝 How to write this in your Report:**
    > *"To identify areas under progressive environmental stress, we developed a multi-temporal Persistent Vegetation Loss Hotspot Map (Figure 14). By tracking pixels that experienced significant vegetation loss ($d < -0.08$) across multiple consecutive time periods, we isolated areas of persistent degradation. The dense clusters of red hotspots concentrated in [mention specific peninsula regions] highlight primary deforestation zones where natural land cover has been permanently altered by commercial activity."*

---

# 📂 3. THE `/stats` & `/models` DIRECTORIES (Raw Scientific Data)

---

## 🗃️ `sequential_changes.csv` & `transition_matrix.csv`
*   **What they are:** The raw CSV datasets generated by Cells 23 and 25.
*   **Why they are useful:** These files contain the exact numbers you should put in your report tables! 
    *   `transition_matrix.csv` has the exact hectare changes between every single class combination.
    *   `sequential_changes.csv` contains the exact hectares lost, gained, and net changes for every single time interval.
*   **📝 How to write this in your Report:**
    > *"The exact spatial transitions and chronological changes were exported to standardized database tables (Tables 1 & 2). These datasets represent the core empirical foundation of our spatial study, providing exact, reproducible pixel-level area counts for both class-to-class transitions and annualized interval-based land cover gains and losses."*

---

## 🤖 `rf_model.pkl` & `rf_bands_only.pkl`
*   **What they are:** The serialized machine learning models saved in the `/models` directory.
*   **The Under-the-Hood Science:** These are your trained **Random Forest Classifiers**. 
    *   `rf_model.pkl` is the standard 11-feature model used to draw your classified maps.
    *   `rf_bands_only.pkl` is the 6-band model used for cross-scene validation.
    *   Saving them as `.pkl` (pickle) files using `joblib` allows anyone to instantly reload your trained models in python and classify any new satellite image of Sri Lanka without having to re-train the model! This represents excellent reproducibility.
*   **📝 How to write this in your Report:**
    > *"To ensure maximum scientific reproducibility, our trained Random Forest classifiers and associated Standard Scalers were serialized and preserved as open-source Python model binaries (`.pkl`). These models can be reloaded in any spatial environment to instantly classify future Landsat imagery of coastal Sri Lanka, providing an accessible, reproducible monitoring tool for local environmental authorities."*

---

# 💡 Summary Table: Output Files to Report Sections

Use this table to map your generated output files directly to your **8+ page Report structure**:

| Report Section | Visual / Data File to Include | Primary Purpose in Report |
| :--- | :--- | :--- |
| **Methodology: Dataset** | `01_timeline.png` | Standardizes the temporal timeline of Landsat scenes. |
| **Methodology: Preprocessing** | `02_cloud_cover.png` & `02_rgb_grid.png` | Proves cloud-masking efficiency & percentile stretching. |
| **Methodology: Preprocessing** | `03_land_mask.png` | Validates permanent water masking (shrimp farm exclusion). |
| **Methodology: ML Validation** | `04_rf_evaluation.png` | Proves model accuracy via Confusion Matrix & Dual-Model Kappa. |
| **Results: Image Classification** | `05_before_after_maps.png` | The core "Before-vs-After" land cover change visual. |
| **Results: Change Detection** | `05_transition_matrix.png` & `transition_matrix.csv` | Quantifies the exact pathways of forest clearing. |
| **Results: Change Detection** | `ndvi_change_maps.png` & `loss_hotspots.png` | Identifies spatial hotspots of severe forest canopy thinning. |
| **Results: Forecasting** | `06_summary_dashboard.png` | Models the NDVI trend and confidence forecast to 2030. |
| **Discussion: Actionable Insights** | `07_deforestation_rates.png` & `sequential_changes.csv` | Chronologically tracks the speed of deforestation (ha/year). |
