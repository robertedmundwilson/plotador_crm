# update ln5 and ln45
import pandas as pd

# Define the file path for the CSV file
file_path = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_raw/HH_Provider_Jul2024.csv'

# Define the columns to include and their new names
columns_to_include = {
    'CMS Certification Number (CCN)': 'CCN',
    'Provider Name': 'Provider_Name',
    'Address': 'Address',
    'City/Town': 'City_Town',
    'ZIP Code': 'Zip',
    'Telephone Number': 'Telephone',
    'DTC Denominator': 'DTC'
}

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Select only the columns specified and rename them
df_filtered = df[list(columns_to_include.keys())].copy()
df_filtered.rename(columns=columns_to_include, inplace=True)

# Convert relevant columns to strings to avoid concatenation issues
df_filtered['Address'] = df_filtered['Address'].astype(str).str.strip()
df_filtered['City_Town'] = df_filtered['City_Town'].astype(str).str.strip()
df_filtered['Zip'] = df_filtered['Zip'].astype(str).str.strip()

# Create a new column combining Address, City_Town, Zip, and "USA"
df_filtered['Full_Address'] = (
    df_filtered['Address'] + ', ' +
    df_filtered['City_Town'] + ', ' +
    df_filtered['Zip'] + ', USA'
)

# Remove any duplicate rows
df_filtered = df_filtered.drop_duplicates()

# Optional: Display the first few entries of Full_Address to check formatting
import IPython.display as display
print(df_filtered['Full_Address'].head(10))

# Define the output file path
output_file = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/HH_Provider_Jul2024_cleaned.csv'

# Save the filtered DataFrame to a new CSV file
df_filtered.to_csv(output_file, index=False)
