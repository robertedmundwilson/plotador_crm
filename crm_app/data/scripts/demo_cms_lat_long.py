import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import googlemaps

# Path to the CSV file
CSV_FILE = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/ALL_CMS_cleaned_ALL.csv'

# Google Maps API Key (Replace 'YOUR_GOOGLE_API_KEY' with your actual API key)
gmaps = googlemaps.Client(key='') #see 1password Google Map API Key

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)

# Filter DataFrame for specific states
df = df[df['State'].isin(['MN', 'WI', 'FL', 'IL', 'IA', 'SD', 'MI', 'ND', 'OH'])]

# Known addresses with manual lat/long (fallback for problematic addresses)
manual_coords = {
    # "1450 N PLEASANT ST, RIPON, WI 54971, USA": (43.829251, -88.832386),
    # Add other addresses here if needed
}

# Function to clean address without removing important location details
def clean_address(address):
    if pd.notnull(address):
        return address.strip()
    return None

# Function to apply clean_address to Full_Address column
def apply_clean_address(row):
    if 'Full_Address' in row and pd.notnull(row['Full_Address']):
        return clean_address(row['Full_Address'])
    return None

# Apply clean_address function to create 'Cleaned Address' column
df['Cleaned Address'] = df.apply(apply_clean_address, axis=1)

# Filter DataFrame for the specific city and get distinct addresses
distinct_addresses = df['Cleaned Address'].dropna().unique()

# Initialize counters
nominatim_success_count = 0
google_success_count = 0
failure_count = 0

# Function to geocode using Google Geocoding API as a fallback
def geocode_with_google(address):
    global google_success_count
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            google_success_count += 1  # Increment counter for successful Google geocoding
            return location['lat'], location['lng']
        else:
            print(f"Google Geocoding failed for address: {address}")
            return None, None
    except Exception as e:
        print(f"Google Geocoding error for address: {address}")
        print(e)
        return None, None

# Function to geocode address with retry mechanism and checking the returned address
def geocode_address(address):
    global nominatim_success_count
    # Check if the address is in the manual_coords dictionary
    if address in manual_coords:
        print(f"Using manual coordinates for address: {address}")
        return manual_coords[address]
    
    # Attempt geocoding using Nominatim
    geolocator = Nominatim(user_agent="dash_app", timeout=10)  # Increased timeout to 10 seconds
    retries = 3  # Number of retries
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address)
            if location:
                nominatim_success_count += 1  # Increment counter for successful Nominatim geocoding
                # Print the returned address to verify it matches the input address
                print(f"Geocoded address using Nominatim: {location.address}")
                return location.latitude, location.longitude
            else:
                print(f"Nominatim failed for address: {address}")
                break  # If Nominatim fails, exit loop and try Google Geocoding API
        except GeocoderTimedOut:
            if attempt < retries - 1:
                print(f"Nominatim timed out for address: {address}. Retrying...")
            else:
                print(f"Nominatim timed out for address: {address}. Maximum retries exceeded.")
                break
        except Exception as e:
            print(f"Nominatim error for address: {address}")
            print(e)
            break
    
    # Fallback to Google Geocoding API if Nominatim fails
    print(f"Falling back to Google Geocoding for address: {address}")
    return geocode_with_google(address)

# Create a DataFrame for the distinct addresses and their coordinates
address_coords = pd.DataFrame(distinct_addresses, columns=['Cleaned Address'])
address_coords[['Latitude', 'Longitude']] = address_coords['Cleaned Address'].apply(
    lambda addr: pd.Series(geocode_address(addr))
)

# Merge the coordinates back to the original DataFrame
df = df.merge(address_coords, on='Cleaned Address', how='left')

# Add geo_lat_long column with proper formatting
df['geo_lat_long'] = df.apply(lambda row: f"{row['Latitude']},{row['Longitude']}" 
                              if pd.notnull(row['Latitude']) and pd.notnull(row['Longitude']) 
                              else None, axis=1)

# Count failures (where both methods returned None)
failure_count = df[df['Latitude'].isnull() & df['Longitude'].isnull()].shape[0]

# Save the updated DataFrame with lat/long back to a CSV file
COORDINATES_CSV = '/Users/robertwilson/CMS_Datafiles/Moments/moments_cms_lat_long_ALL.csv'
df.to_csv(COORDINATES_CSV, index=False)

# Save a second file with rows where lat/long was not generated
failed_coords_df = df[df['Latitude'].isnull() & df['Longitude'].isnull()]
FAILED_COORDS_CSV = '/Users/robertwilson/CMS_Datafiles/Moments/failed_moments_cms_lat_long_ALL.csv'
failed_coords_df.to_csv(FAILED_COORDS_CSV, index=False)

# Print results
print(f"Total geocoded addresses using Nominatim: {nominatim_success_count}")
print(f"Total geocoded addresses using Google Geocoding: {google_success_count}")
print(f"Total addresses where geocoding failed: {failure_count}")

# Rename 'Beds' column to 'Potential'
df.rename(columns={'Beds': 'Potential'}, inplace=True)

# Create a new column 'Actual' with empty strings
df['Actual'] = ''
