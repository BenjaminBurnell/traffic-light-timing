import pandas as pd
import json

# 1. Load your two files
timing_df = pd.read_csv('traffic-signals-timing.csv')
locations_df = pd.read_csv('Traffic Signal - 4326.csv')

# 2. Merge them together using TCS and PX
merged_df = pd.merge(timing_df, locations_df, left_on='TCS', right_on='PX', how='inner')

# 3. Functions to extract Latitude and Longitude from the JSON geometry string
def extract_lon(geom_str):
    try:
        return json.loads(geom_str)['coordinates'][0][0]
    except:
        return None

def extract_lat(geom_str):
    try:
        return json.loads(geom_str)['coordinates'][0][1]
    except:
        return None

# Apply the functions to create new lat and lon columns
merged_df['lon'] = merged_df['geometry'].apply(extract_lon)
merged_df['lat'] = merged_df['geometry'].apply(extract_lat)

# 4. Create a clean 'name' column using the street names
merged_df['name'] = merged_df['MAIN_STREET'].astype(str) + " & " + merged_df['SIDE1_STREET'].astype(str)

# 5. Clean up the file to keep only what your JavaScript needs
# (You can add more columns to this list if you want to use them later)
final_df = merged_df[['TCS', 'name', 'lat', 'lon', 'PHASE', 'PHASE_STATUS', 'PHASE_STATUS_TEXT']]

# 6. Save the final usable file
final_df.to_csv('traffic-signals-combined.csv', index=False)

print("Merge complete! Saved to traffic-signals-combined.csv")