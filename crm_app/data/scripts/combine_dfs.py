import pandas as pd
import os

# Define paths
input_dir = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/'
output_file = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/ALL_CMS_cleaned.csv'

# List of CSV files to combine
csv_files = [
    'DAC_NationalDownloadableFile_cleaned.csv',
    'HH_Provider_Jul2024_cleaned.csv',
    'Hospice_Provider_Aug2024_cleaned.csv',
    'Hospital_General_Information_cleaned.csv',
    'NH_ProviderInfo_Aug2024_cleaned.csv'
]

column_mappings = {
    'DAC_NationalDownloadableFile': {
        'Type_1': 'Type_1',
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
        'Telephone Number': 'Telephone',
        'Full Address': 'Full_Address'
    },
    'HH_Provider': {
        'Type_1': 'Type_1',
        'CMS Certification Number (CCN)': 'CCN',
        'Provider Name': 'Provider_Name',
        'Address': 'Address',
        'City/Town': 'City_Town',
        'ZIP Code': 'Zip',
        'Telephone Number': 'Telephone',
        'DTC Denominator': 'DTC',
        'Full Address': 'Full_Address'
    },
    'Hospice_Provider': {
        'Type_1': 'Type_1',
        'NPI': 'NPI',
        'Provider Last Name': 'Provider_Last',
        'Provider First Name': 'Provider_First',
        'Cred': 'Cred',
        'pri_spec': 'pri_spec',
        'Facility Name': 'Facility_Name',
        'Address': 'Address',
        'City/Town': 'City_Town',
        'State': 'State',
        'ZIP Code': 'Zip',
        'Telephone Number': 'Telephone',
        'Full Address': 'Full_Address'
    },
    'Hospital_General_Information': {
        'Type_1': 'Type_1',
        'Facility ID': 'Facility_ID',
        'Facility Name': 'Facility_Name',
        'Address': 'Address',
        'City/Town': 'City_Town',
        'State': 'State',
        'ZIP Code': 'Zip',
        'County/Parish': 'County',
        'Telephone Number': 'Telephone',
        'Full Address': 'Full_Address'
    },
    'NH_ProviderInfo': {
        'Type_1': 'Type_1',
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
        'Longitude': 'Longitude',
        'Full Address': 'Full_Address'
    }
}

# List of valid pri_spec values
valid_pri_spec = [
    'ADULT CONGENITAL HEART DISEASE (ACHD)',
    'ADVANCED HEART FAILURE AND TRANSPLANT CARDIOLOGY',
    'CARDIOVASCULAR DISEASE (CARDIOLOGY)',
    'CERTIFIED CLINICAL NURSE SPECIALIST (CNS)',
    'CLINICAL SOCIAL WORKER',
    'CRITICAL CARE (INTENSIVISTS)',
    'EMERGENCY MEDICINE',
    'ENDOCRINOLOGY',
    'FAMILY PRACTICE',
    'GASTROENTEROLOGY',
    'GENERAL PRACTICE',
    'GERIATRIC MEDICINE',
    'GYNECOLOGICAL ONCOLOGY',
    'HEMATOLOGY',
    'HEMATOLOGY/ONCOLOGY',
    'HOSPICE/PALLIATIVE CARE',
    'HOSPITALIST',
    'INFECTIOUS DISEASE',
    'INTERNAL MEDICINE',
    'INTERVENTIONAL CARDIOLOGY',
    'INTERVENTIONAL PAIN MANAGEMENT',
    'MEDICAL ONCOLOGY',
    'NEPHROLOGY',
    'NEUROLOGY',
    'NURSE PRACTITIONER',
    'PHYSICAL MEDICINE AND REHABILITATION',
    'PHYSICAL THERAPY',
    'PHYSICIAN ASSISTANT',
    'PULMONARY DISEASE',
    'RADIATION ONCOLOGY',
    'RHEUMATOLOGY'
]

# Read each CSV file into a DataFrame, rename columns, and store in a list
dataframes = []
for file in csv_files:
    file_path = os.path.join(input_dir, file)
    df = pd.read_csv(file_path, dtype={'NPI': str, 'Zip': str})
    
    # Get the file type from the filename
    file_type = file.split('_cleaned.csv')[0].split('_')[0]
    if file_type == 'NH':
        file_type = 'NH_ProviderInfo'
    elif file_type == 'Hospital':
        file_type = 'Hospital_General_Information'
    elif file_type == 'DAC':
        file_type = 'DAC_NationalDownloadableFile'
    elif file_type == 'HH':
        file_type = 'HH_Provider'
    elif file_type == 'Hospice':
        file_type = 'Hospice_Provider'
    
    # Combine Provider_Address into Address for all file types
    if 'Provider_Address' in df.columns:
        df['Address'] = df['Provider_Address']
        df = df.drop('Provider_Address', axis=1)
    elif 'Provider Address' in df.columns:
        df['Address'] = df['Provider Address']
        df = df.drop('Provider Address', axis=1)
    
    # Rename columns based on the mapping
    df = df.rename(columns=column_mappings[file_type])
    
    # Filter 'DAC_NationalDownloadableFile' by specific 'pri_spec' values
    if file_type == 'DAC_NationalDownloadableFile':
        if 'pri_spec' in df.columns:
            df = df[df['pri_spec'].notnull() & df['pri_spec'].isin(valid_pri_spec)]
    
    # Consolidate 'Facility Name' and 'Provider Name' into 'Facility_Name'
    if 'Provider_Name' in df.columns and 'Facility_Name' not in df.columns:
        df['Facility_Name'] = df['Provider_Name']
        df = df.drop('Provider_Name', axis=1)
    elif 'Provider_Name' in df.columns and 'Facility_Name' in df.columns:
        df['Facility_Name'] = df['Facility_Name'].fillna(df['Provider_Name'])
        df = df.drop('Provider_Name', axis=1)
    
    # Drop specified columns
    columns_to_drop = ['CCN', 'DTC', 'Location', 'Latitude', 'Longitude']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
    
    dataframes.append(df)

# Combine all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Remove duplicate rows based on all columns
combined_df = combined_df.drop_duplicates()

# Ensure 'City_Town', 'State', and 'Zip' columns are present
required_columns = ['City_Town', 'State', 'Zip']
for col in required_columns:
    if col not in combined_df.columns:
        print(f"Warning: '{col}' column is missing from the combined data.")

# Convert Zip to string and keep only the first 5 digits
combined_df['Zip'] = combined_df['Zip'].astype(str).str[:5]

# Create a subset of the data including only zip codes 78751 and 78703
subset_df = combined_df[combined_df['Zip'].isin(['78751', '78703'])]

# Save the full combined DataFrame to a new CSV file
combined_df.to_csv(output_file, index=False)

# Save the subset DataFrame to a new CSV file
subset_output_file = output_file.replace('.csv', '_subset.csv')
subset_df.to_csv(subset_output_file, index=False)

print(f"Combined data has been saved to {output_file}")
print(f"Total number of rows in combined data: {len(combined_df)}")
print(f"Columns in the combined DataFrame: {combined_df.columns.tolist()}")
print(f"Rows per Type_1 category in full dataset:")
print(combined_df['Type_1'].value_counts())

print(f"\nSubset data has been saved to {subset_output_file}")
print(f"Total number of rows in subset data: {len(subset_df)}")
print(f"Rows per Type_1 category in subset:")
print(subset_df['Type_1'].value_counts())
print(f"\nZip code distribution in subset:")
print(subset_df['Zip'].value_counts())
