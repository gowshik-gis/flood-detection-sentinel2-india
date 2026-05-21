# 🌊 Flood Detection using Sentinel-2 in India

## Overview
This project detects flooded areas in India using **Sentinel-2 satellite imagery** and the **Modified Normalized Difference Water Index (MNDWI)**. It compares pre-flood and during-flood satellite images to identify newly submerged land.

## Tools Used (All Free)
- **Python** — Programming language
- **Google Earth Engine** — Cloud-based satellite data processing
- **geemap** — Interactive mapping
- **Sentinel-2** — ESA satellite imagery (10m resolution)
- **MNDWI** — Water body detection index

## Methodology
1. **Data Collection**: Retrieved Sentinel-2 Level-2A images from Google Earth Engine
2. **Cloud Masking**: Used Scene Classification Layer (SCL) to remove clouds
3. **Index Calculation**: Applied MNDWI = (Green - SWIR1) / (Green + SWIR1)
4. **Change Detection**: Subtracted pre-flood water mask from during-flood water mask
5. **Area Calculation**: Computed flooded area in hectares

## Key Results
- **Location**: Assam, India
- **Period Analyzed**: April 2024 (pre-flood) vs June 2024 (flood)
- **Output**: Interactive HTML map + GeoTIFF export
- **Flood Extent**: Calculated in hectares using 10m resolution data

## Files
- `flood_detection.py` — Main analysis script
- `authenticate.py` — One-time GEE authentication
- `outputs/flood_map.html` — Interactive map (open in browser)

## How to Run
1. Install Python 3.11
2. `pip install -r requirements.txt`
3. Run `authenticate.py` once
4. Run `flood_detection.py`

## Author
Gowshik P — Aspiring Geospatial Data Analyst
