<!DOCTYPE html>
<html>
<head>
    <title>Flood Detection | Sentinel-2 India</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
        img { max-width: 100%; border-radius: 8px; }
        .tech { background: #f0f0f0; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🌊 Flood Detection using Sentinel-2 in India</h1>
    <p><strong>Geospatial Data Analysis Project</strong></p>
    
    <h2>Problem</h2>
    <p>India's monsoon floods affect millions annually. Traditional ground surveys are slow and dangerous during active flooding.</p>
    
    <h2>Solution</h2>
    <p>Automated satellite-based flood mapping using Python and Google Earth Engine, processing Sentinel-2 imagery in the cloud.</p>
    
    <div class="tech">
        <h3>Technologies Used</h3>
        <ul>
            <li>Python + Google Earth Engine API</li>
            <li>Sentinel-2 MSI (10m resolution)</li>
            <li>MNDWI Water Index</li>
            <li>Cloud masking (SCL band)</li>
            <li>Change detection algorithms</li>
        </ul>
    </div>
    
    <h2>Results</h2>
    <p>Successfully mapped flood extent in Assam, India comparing April 2024 (pre-flood) vs June 2024 (monsoon).</p>
    <p>Calculated flooded area in hectares with 10-meter spatial accuracy.</p>
    
    <h2>Outputs</h2>
    <ul>
        <li>Interactive HTML map with layer toggles</li>
        <li>GeoTIFF raster export for GIS software</li>
        <li>Automated area statistics report</li>
    </ul>
    
    <p><a href="https://github.com/gowshik-gis/flood-detection-sentinel2-india">View Code on GitHub →</a></p>
</body>
</html>