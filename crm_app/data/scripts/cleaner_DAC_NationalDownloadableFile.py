# update ln 7 ln75 ln76


import pandas as pd
import os

# Define the file path for the CSV file
file_path = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_raw/DAC_NationalDownloadableFile.csv'

# Define data types for columns to avoid mixed type warnings
dtype_spec = {
    'NPI': str,
    'Provider Last Name': str,
    'Provider First Name': str,
    'Cred': str,
    'pri_spec': str,
    'Facility Name': str,
    'adr_ln_1': str,
    'City/Town': str,
    'State': str,
    'ZIP Code': str,
    'Telephone Number': str
}

# Read the CSV file into a DataFrame with specified data types
df = pd.read_csv(file_path, dtype=dtype_spec, low_memory=False)

# Print column names to verify
print("Actual column names in the CSV file:")
print(df.columns.tolist())

# Define the columns to include and their new names
columns_to_include = {
    'NPI': 'NPI',
    'Provider Last Name': 'Provider_Last',
    'Provider First Name': 'Provider_First',
    'Cred': 'Cred',
    'pri_spec': 'pri_spec',
    'Facility Name': 'Facility_Name',
    'adr_ln_1': 'Address',
    'City/Town': 'City_Town',
    'State': 'State',
    'ZIP Code': 'Zip',
    'Telephone Number': 'Telephone'
}

# Check if all required columns are present in the DataFrame
missing_columns = [col for col in columns_to_include.keys() if col not in df.columns]
if missing_columns:
    print(f"Missing columns: {missing_columns}")

# Proceed if no columns are missing
if not missing_columns:
    # Select only the columns specified and rename them
    df_filtered = df[list(columns_to_include.keys())].copy()
    df_filtered.rename(columns=columns_to_include, inplace=True)

    # Add new column 'Type_1' at the beginning with all values as 'PHYSICIAN'
    df_filtered.insert(0, 'Type_1', 'CMS - PHYSICIAN')

    # Remove last four digits from Zip values
    df_filtered['Zip'] = df_filtered['Zip'].astype(str).str[:5]

    # Create the Full_Address column
    df_filtered['Full_Address'] = (
        df_filtered['Address'].astype(str) + ', ' +
        df_filtered['City_Town'].astype(str) + ', ' +
        df_filtered['State'].astype(str) + ' ' +
        df_filtered['Zip'].astype(str) + ', USA'
    )

    # Clean up Full_Address column
    df_filtered['Full_Address'] = df_filtered['Full_Address'].str.strip()
    # Remove any duplicate rows
    df_filtered = df_filtered.drop_duplicates()

    # Print the first 10 rows of the filtered DataFrame for inspection
    import IPython.display as display
    display.display(df_filtered.head(10))

    # Define the output file path
    output_dir = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/'
    output_file = os.path.join(output_dir, 'DAC_NationalDownloadableFile_cleaned.csv')

    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the filtered DataFrame to a new CSV file
    df_filtered.to_csv(output_file, index=False)

    print(f"Filtered data has been saved to {output_file}")
else:
    print("Data processing cannot continue due to missing columns.")
