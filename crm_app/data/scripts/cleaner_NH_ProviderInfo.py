#Update ln 5 and ln40
import pandas as pd

# Define the file path for the CSV file
file_path = '/Users/robertwilson/git/plotador_crm/crm_app/data/files/Sept_2024/CMS_raw/NH_ProviderInfo_Aug2024.csv'

# Define the columns to include and their new names
columns_to_include = {
    'CMS Certification Number (CCN)': 'CCN',
    'Provider Name': 'Provider_Name',
    'Provider Address': 'Provider_Address',
    'City/Town': 'City_Town',
    'State': 'State',
    'ZIP Code': 'Zip',
    'Location': 'Location',
    'Telephone Number': 'Telephone',
    'County/Parish': 'County',
    'Number of Certified Beds': 'Beds',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude'
}

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Select only the columns specified
df_filtered = df[list(columns_to_include.keys())].copy()

# Rename the columns
df_filtered.rename(columns=columns_to_include, inplace=True)

# Remove duplicate rows
df_filtered = df_filtered.drop_duplicates()

# Print the first 10 rows of the filtered DataFrame
import IPython.display as display
display.display(df_filtered.head(10))

# Optionally, save the filtered DataFrame to a new CSV file
output_file = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/NH_ProviderInfo_Aug2024_cleaned.csv'

df_filtered.to_csv(output_file, index=False)
