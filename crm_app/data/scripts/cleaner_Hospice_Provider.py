# update ln5 and ln66
import pandas as pd

# Define the file path for the CSV file
file_path = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_raw/Hospice_Provider_Aug2024.csv'

# Define the columns to include and their new names
columns_to_include = {
    'CMS Certification Number (CCN)': 'CCN',
    'Facility Name': 'Facility_Name',
    'Address Line 1': 'Address',
    'City/Town': 'City_Town',
    'State': 'State',
    'ZIP Code': 'Zip',
    'County/Parish': 'County',
    'Telephone Number': 'Telephone'
}

# Read the CSV file into a DataFrame with specified data types
dtype_dict = {
    'CMS Certification Number (CCN)': str,
    'Facility Name': str,
    'Address Line 1': str,
    'City/Town': str,
    'State': str,
    'ZIP Code': str,
    'County/Parish': str,
    'Telephone Number': str
}
df = pd.read_csv(file_path, dtype=dtype_dict)

# Select only the columns specified and rename them
df_filtered = df.loc[:, list(columns_to_include.keys())].copy()
df_filtered.rename(columns=columns_to_include, inplace=True)

df_filtered.insert(0, 'Type_1', 'CMS - Hospice')

# Convert relevant columns to strings and clean them up
df_filtered['Address'] = df_filtered['Address'].astype(str).str.strip()
df_filtered['City_Town'] = df_filtered['City_Town'].astype(str).str.strip()
df_filtered['State'] = df_filtered['State'].astype(str).str.strip()
df_filtered['Zip'] = df_filtered['Zip'].astype(str).str.strip()

# Create a new column combining Address, City_Town, State, Zip, and "USA"
df_filtered['Full_Address'] = (
    df_filtered['Address'].str.strip() + ', ' +
    df_filtered['City_Town'].str.strip() + ', ' +
    df_filtered['State'].str.strip() + ' ' +
    df_filtered['Zip'].str.strip() + ', USA'
)

# Clean up the Full_Address column further
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
output_file = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/Hospice_Provider_Aug2024_cleaned.csv'

# Save the filtered DataFrame to a new CSV file
df_filtered.to_csv(output_file, index=False)
