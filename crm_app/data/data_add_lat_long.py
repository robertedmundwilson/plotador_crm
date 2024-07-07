import pandas as pd
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Determine the path to the CSV file
current_directory = os.path.dirname(__file__)
CSV_FILE = os.path.join(current_directory, 'provider_july7.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)
df = df.drop(columns=['Latitude', 'Longitude'], errors='ignore')

# Function to clean address
def clean_address(address):
    if pd.notnull(address):
        # Remove anything after a comma
        address = address.split(',')[0]
        # Remove specific keywords and anything after them
        for keyword in ['STE', 'SUITE', 'BUILDING', 'UNIT']:
            address = address.split(keyword)[0]
        return address.strip()
    return None

# Function to apply clean_address to relevant columns
def apply_clean_address(row):
    for col in ['Address', 'Address Line 1', 'Provider Address','adr_ln_1']:
        if col in row and pd.notnull(row[col]):
            return clean_address(row[col])
    return None

# Apply clean_address function to create 'Cleaned Address' column
df['Cleaned Address'] = df.apply(apply_clean_address, axis=1)

# Filter DataFrame for the specific city and get distinct addresses
df_subset = df[df['City/Town'] == 'CHARLESTON'].copy()
distinct_addresses = df_subset['Cleaned Address'].dropna().unique()

# Function to geocode address with retry mechanism
def geocode_address(address):
    geolocator = Nominatim(user_agent="dash_app", timeout=10)  # Increased timeout to 10 seconds
    retries = 3  # Number of retries
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                print(f"Geocoding failed for address: {address}")
                return None, None
        except GeocoderTimedOut:
            if attempt < retries - 1:
                print(f"Geocoding timed out for address: {address}. Retrying...")
            else:
                print(f"Geocoding timed out for address: {address}. Maximum retries exceeded.")
                return None, None
        except Exception as e:
            print(f"Geocoding error for address: {address}")
            print(e)
            return None, None
    return None, None

# Create a DataFrame for the distinct addresses and their coordinates
address_coords = pd.DataFrame(distinct_addresses, columns=['Cleaned Address'])
address_coords[['Latitude', 'Longitude']] = address_coords['Cleaned Address'].apply(
    lambda addr: pd.Series(geocode_address(addr))
)

# Merge the coordinates back to the original DataFrame
df_subset = df_subset.merge(address_coords, on='Cleaned Address', how='left')

# Save to CSV
COORDINATES_CSV = os.path.join(current_directory, 'provider_july7_enhanced.csv')
df_subset.to_csv(COORDINATES_CSV, index=False)
