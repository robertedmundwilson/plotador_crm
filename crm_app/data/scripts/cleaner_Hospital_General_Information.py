# update ln5 and ln56

import pandas as pd

# Define the file path for the CSV file
file_path = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_raw/Hospital_General_Information.csv'

# Define the columns to include and their new names
columns_to_include = {
    'Facility ID': 'Facility_ID',
    'Facility Name': 'Facility_Name',
    'Address': 'Address',
    'City/Town': 'City_Town',
    'State': 'State',
    'ZIP Code': 'Zip',
    'County/Parish': 'County',
    'Telephone Number': 'Telephone'
}

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Select only the columns specified and rename them
df_filtered = df.loc[:, list(columns_to_include.keys())].copy()
df_filtered.rename(columns=columns_to_include, inplace=True)

# Convert relevant columns to strings to avoid concatenation issues
df_filtered['Address'] = df_filtered['Address'].astype(str).str.strip()
df_filtered['City_Town'] = df_filtered['City_Town'].astype(str).str.strip()
df_filtered['State'] = df_filtered['State'].astype(str).str.strip()
df_filtered['Zip'] = df_filtered['Zip'].astype(str).str.strip()

# Create a new column combining Address, City_Town, State, Zip, and "USA"
df_filtered['Full_Address'] = (
    df_filtered['Address'] + ', ' +
    df_filtered['City_Town'] + ', ' +
    df_filtered['State'] + ' ' +
    df_filtered['Zip'] + ', USA'
)

# Clean up the Full_Address column
df_filtered['Full_Address'] = (
    df_filtered['Full_Address']
    .str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with a single space
    .str.replace(r'\s*,\s*', ', ', regex=True)  # Ensure single space after commas
    .str.strip()  # Remove leading and trailing spaces
)

# Optional: Remove any duplicate rows
df_filtered = df_filtered.drop_duplicates()

# Print the first 10 rows of the filtered DataFrame for inspection
import IPython.display as display
display.display(df_filtered.head(10))

# Define the output file path
output_file = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/Hospital_General_Information_cleaned.csv'

# Save the filtered DataFrame to a new CSV file
df_filtered.to_csv(output_file, index=False)
