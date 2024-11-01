import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import googlemaps

# Path to the CSV file
fips_file = '/Users/robertwilson/CMS_Datafiles/US_FIPS_Codes.csv'
zip_county_file = '/Users/robertwilson/CMS_Datafiles/ZIP_COUNTY_062024.csv'
# CSV_FILE = '/Users/robertwilson/CMS_Datafiles/Demo/Demo_Accounts.csv'
CSV_FILE = '/Users/robertwilson/CMS_Datafiles/Moments/October_SHORT.csv'

# Google Maps API Key (Replace 'YOUR_GOOGLE_API_KEY' with your actual API key)
gmaps = googlemaps.Client(key='AIzaSyATO9diFoJqVSCqa1VKPlOSYTf-RC2nGag')

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)

# Drop existing Latitude and Longitude columns if they exist
df = df.drop(columns=['Latitude', 'Longitude'], errors='ignore')

# Read FIPS and ZIP-County data
fips_df = pd.read_csv(fips_file)
fips_df.columns = fips_df.columns.str.strip()  # Strip whitespace from column names
zip_county_df = pd.read_csv(zip_county_file, dtype={'COUNTY': str, 'ZIP': str})

# Format FIPS and ZIP-County data
fips_df['fips_code'] = fips_df['FIPS State'].astype(str).str.zfill(2) + fips_df['FIPS County'].astype(str).str.zfill(3)
zip_county_df['county'] = zip_county_df['COUNTY'].str.zfill(5)

# Create final ZIP-County lookup and ensure unique county per ZIP
zip_county_final = (
    zip_county_df[['ZIP', 'county']]
    .groupby('ZIP', as_index=False)
    .first()  # Keep the first county associated with each ZIP
)

zip_county_final = pd.merge(
    zip_county_final,
    fips_df[['fips_code', 'County Name']],
    left_on='county', right_on='fips_code',
    how='left'
)

# Convert 'Zip' column to string type to match 'ZIP' column
df['Zip'] = df['Zip'].astype(str)
# Merge the DataFrames
df = pd.merge(df, zip_county_final[['ZIP', 'County Name']], left_on='Zip', right_on='ZIP', how='left')



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

# Function to apply clean_address to addr_full column
def apply_clean_address(row):
    if 'addr_full' in row and pd.notnull(row['addr_full']):
        return clean_address(row['addr_full'])
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
failure_count = df[df['geo_lat_long'].isnull()].shape[0]

df = df.drop(columns=['ZIP', 'Cleaned Address'])

# Save the updated DataFrame with lat/long back to a CSV file
COORDINATES_CSV = '/Users/robertwilson/CMS_Datafiles/Moments/October_SHORT_lat_long.csv'
df.to_csv(COORDINATES_CSV, index=False)

# Save a second file with rows where lat/long was not generated
failed_coords_df = df[df['geo_lat_long'].isnull()]
FAILED_COORDS_CSV = '/Users/robertwilson/CMS_Datafiles/Moments/failed_October_SHORT_lat_long.csv'
failed_coords_df.to_csv(FAILED_COORDS_CSV, index=False)

# Print results
print(f"Total geocoded addresses using Nominatim: {nominatim_success_count}")
print(f"Total geocoded addresses using Google Geocoding: {google_success_count}")
print(f"Total addresses where geocoding failed: {failure_count}")
