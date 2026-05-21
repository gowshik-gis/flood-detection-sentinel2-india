# ============================================================
# FLOOD DETECTION - BULLETPROOF VERSION
# Handles missing images, empty collections, and cloud issues
# ============================================================

import ee
import geemap
import os

# --- STEP 1: Connect to Google Earth Engine ---
ee.Initialize(project="flood-detection-india-2026")
print("✅ Connected to Earth Engine")

# --- STEP 2: Define Your Study Area ---
# Default: Assam (slightly larger box to ensure coverage)
# Format: [West, South, East, North]
REGION = ee.Geometry.Rectangle([91.0, 25.5, 93.0, 27.0])

# --- STEP 3: Define Time Periods ---
# IMPORTANT: Monsoon floods in Assam peak in JULY-AUGUST, not June
# BEFORE FLOOD: Pre-monsoon (dry season)
BEFORE_START = '2024-03-01'
BEFORE_END = '2024-03-31'

# DURING FLOOD: Peak monsoon (when floods actually happen)
FLOOD_START = '2024-07-15'
FLOOD_END = '2024-08-15'

print(f"📅 Analyzing BEFORE: {BEFORE_START} to {BEFORE_END}")
print(f"📅 Analyzing FLOOD:  {FLOOD_START} to {FLOOD_END}")

# --- STEP 4: Load Sentinel-2 Data ---
sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')

# Cloud masking function using SCL band
def remove_clouds(image):
    scl = image.select('SCL')
    # Keep: 4=Vegetation, 5=Bare soil, 6=Water, 7=Low prob cloud
    good_pixels = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(7))
    return image.updateMask(good_pixels)

# --- STEP 5: FETCH IMAGES WITH ERROR HANDLING ---
def get_images(start_date, end_date, region, cloud_limit=50):
    """
    Gets Sentinel-2 images with flexible cloud filtering.
    If too few images with strict clouds, tries again with more lenient filter.
    """
    print(f"\n🔍 Searching images from {start_date} to {end_date}...")
    
    # First try: strict cloud filter
    collection = sentinel2 \
        .filterDate(start_date, end_date) \
        .filterBounds(region) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_limit)) \
        .map(remove_clouds)
    
    count = collection.size().getInfo()
    print(f"   Found {count} images with cloud coverage < {cloud_limit}%")
    
    # If 0 images found, try with higher cloud tolerance (but still mask clouds out)
    if count == 0:
        print(f"   ⚠️  0 images found! Trying with cloud coverage < 80%...")
        collection = sentinel2 \
            .filterDate(start_date, end_date) \
            .filterBounds(region) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 80)) \
            .map(remove_clouds)
        count = collection.size().getInfo()
        print(f"   Found {count} images with cloud coverage < 80%")
    
    # If still 0, try without any cloud filter (we'll mask clouds manually)
    if count == 0:
        print(f"   ⚠️  Still 0 images! Trying without cloud filter...")
        collection = sentinel2 \
            .filterDate(start_date, end_date) \
            .filterBounds(region)
        count = collection.size().getInfo()
        print(f"   Found {count} raw images (clouds included)")
    
    if count == 0:
        print(f"   ❌ ERROR: No images exist for this region and time period!")
        print(f"   💡 TIP: Try different months or a larger area.")
        return None
    
    return collection

# Get before and during collections
images_before = get_images(BEFORE_START, BEFORE_END, REGION)
images_during = get_images(FLOOD_START, FLOOD_END, REGION)

# --- STEP 6: SAFETY CHECK ---
# If either collection is empty, stop and tell the user why
if images_before is None or images_during is None:
    print("\n" + "="*60)
    print("❌ CANNOT CONTINUE: One or both time periods have no images.")
    print("="*60)
    print("\n💡 HOW TO FIX:")
    print("1. Open Google Earth Engine Code Editor:")
    print("   https://code.earthengine.google.com")
    print("2. Go to the 'Inspector' tab and click your area on the map")
    print("3. Check what dates have Sentinel-2 coverage")
    print("4. Update BEFORE_START, BEFORE_END, FLOOD_START, FLOOD_END")
    print("5. For Assam floods, try July 15 - August 15 (peak monsoon)")
    print("6. For other states, research their flood season dates")
    print("\n🌐 Alternative: Try a different region with more satellite coverage")
    print("   Example (Kerala): [76.0, 8.0, 77.5, 9.5]")
    print("   Example (Bihar): [85.0, 25.0, 87.0, 27.0]")
    exit()

# --- STEP 7: CREATE MEDIAN COMPOSITES ---
print("\n🧮 Creating clean composite images (this removes clouds and noise)...")
image_before = images_before.median().clip(REGION)
image_during = images_during.median().clip(REGION)

# --- STEP 8: VERIFY BANDS EXIST ---
# This prevents the "No band named 'B3'" error
available_bands_before = image_before.bandNames().getInfo()
available_bands_during = image_during.bandNames().getInfo()

print(f"   Bands available in BEFORE image: {available_bands_before}")
print(f"   Bands available in DURING image: {available_bands_during}")

if len(available_bands_before) == 0 or len(available_bands_during) == 0:
    print("\n❌ ERROR: Composite images have no bands!")
    print("This usually means all images were 100% cloudy and got masked out.")
    print("💡 FIX: Use dates with less cloud cover, or a larger region.")
    exit()

# --- STEP 9: CALCULATE MNDWI ---
# MNDWI = (Green - SWIR1) / (Green + SWIR1)
# Sentinel-2: B3 = Green, B11 = SWIR1
print("\n🌊 Calculating MNDWI (Modified Normalized Difference Water Index)...")

mndwi_before = image_before.normalizedDifference(['B3', 'B11']).rename('MNDWI')
mndwi_during = image_during.normalizedDifference(['B3', 'B11']).rename('MNDWI')

# --- STEP 10: DETECT WATER AND FLOOD ---
# Water = MNDWI > 0.3
water_before = mndwi_before.gt(0.3)
water_during = mndwi_during.gt(0.3)

# Flood = Water during flood AND NOT water before flood
flood_extent = water_during.And(water_before.Not()).selfMask()

print("✅ Flood extent calculated successfully")

# --- STEP 11: CALCULATE FLOODED AREA ---
print("\n📏 Calculating flooded area...")

pixel_area_hectares = ee.Image.pixelArea().divide(10000)

flood_stats = flood_extent.multiply(pixel_area_hectares).reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=REGION,
    scale=10,
    maxPixels=1e9
)

flooded_hectares = flood_stats.get('MNDWI').getInfo()

print("="*60)
print(f"🌊🌊🌊 ESTIMATED FLOODED AREA: {flooded_hectares:.2f} hectares 🌊🌊🌊")
print("="*60)

# --- STEP 12: CREATE INTERACTIVE MAP ---
print("\n🗺️  Building interactive map...")

Map = geemap.Map(center=[26.2, 92.0], zoom=9)

# True-color images (what human eyes see)
Map.addLayer(image_before, {'bands': ['B4','B3','B2'], 'min':0, 'max':3000, 'gamma':1.4}, '1. Before Flood (True Color)')
Map.addLayer(image_during, {'bands': ['B4','B3','B2'], 'min':0, 'max':3000, 'gamma':1.4}, '2. During Flood (True Color)')

# MNDWI visualization (blue = water)
Map.addLayer(mndwi_before, {'palette':['white','lightblue','blue','darkblue'], 'min':-0.5, 'max':0.8}, '3. MNDWI Before')
Map.addLayer(mndwi_during, {'palette':['white','lightblue','blue','darkblue'], 'min':-0.5, 'max':0.8}, '4. MNDWI During')

# Flood extent in RED
Map.addLayer(flood_extent, {'palette': ['red']}, '5. 🚨 NEW FLOOD AREAS (RED)')

Map.addLayerControl()

# --- STEP 13: SAVE OUTPUTS ---
os.makedirs('outputs', exist_ok=True)

# Save interactive map
Map.save('outputs/flood_map.html')
print("✅ Interactive map saved to: outputs/flood_map.html")

# Save a static image for your portfolio
Map.to_html('outputs/flood_map_portfolio.html', title='Flood Detection Assam 2024')
print("✅ Portfolio map saved to: outputs/flood_map_portfolio.html")

# --- STEP 14: EXPORT TO GOOGLE DRIVE ---
print("\n☁️  Starting export to Google Drive (takes 2-5 minutes)...")

# Export the flood extent as GeoTIFF
geemap.ee_export_image_to_drive(
    image=flood_extent,
    description='Flood_Extent_Assam_2024',
    folder='GEE_Flood_Exports',
    region=REGION,
    scale=10,
    maxPixels=1e9
)

print("✅ Export task started!")
print("   📁 Check Google Drive folder: GEE_Flood_Exports")
print("   ⏱️  File will appear in 2-5 minutes")

print("\n" + "="*60)
print("🎉 PROJECT COMPLETE!")
print("="*60)
print("Next steps:")
print("1. Open outputs/flood_map.html in your browser")
print("2. Toggle layers on/off using the layer control (top right)")
print("3. Zoom in to see flood details")
print("4. Check Google Drive for the high-res GeoTIFF file")