import pandas as pd
import os
from geopy.geocoders import Nominatim

# Determine the path to the CSV file
current_directory = os.path.dirname(__file__)
CSV_FILE = os.path.join(current_directory, 'doc_clinicians_SC.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)

# Function to geocode address
def geocode_address(row):
    adr_ln_1 = row['adr_ln_1']
    city = row['City/Town']
    state = row['State']
    zip_code = str(row['ZIP Code'])[:-4]  # Remove last 4 digits from ZIP Code

    # Construct full address
    full_address = f"{adr_ln_1}, {city}, {state} {zip_code}"

    # Geocode using Nominatim
    geolocator = Nominatim(user_agent="dash_app")  # Replace with your user agent name
    try:
        location = geolocator.geocode(full_address)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Geocoding failed for address: {full_address}")
            return None, None
    except Exception as e:
        print(f"Geocoding error for address: {full_address}")
        print(e)
        return None, None

coordinates = df[df['City/Town'] == 'CHARLESTON'].apply(geocode_address, axis=1)
df_subset = df[df['City/Town'] == 'CHARLESTON']

# Add Latitude and Longitude columns
df_subset['Latitude'] = [coord[0] for coord in coordinates]
df_subset['Longitude'] = [coord[1] for coord in coordinates]

# Save to CSV
COORDINATES_CSV = os.path.join(current_directory, 'doc_clinicians_SC_enhanced.csv')
df_subset.to_csv(COORDINATES_CSV, index=False)
