import ee

print("🔐 A browser window will open. Sign in with your Google account.")
print("🔐 Copy the code shown and paste it back here in VS Code terminal.")

ee.Authenticate()

ee.Initialize(project="flood-detection-india-2026")

print("✅ SUCCESS! You are now connected to Google Earth Engine.")
print("✅ You do NOT need to run this file again.")