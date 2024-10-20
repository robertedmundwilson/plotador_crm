import pandas as pd
import os

# Define paths for input and output
input_dir = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/'
output_file = '/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/ALL_CMS_cleaned.csv'
fips_file = '/Users/robertwilson/CMS_Datafiles/US_FIPS_Codes.csv'
zip_county_file = '/Users/robertwilson/CMS_Datafiles/ZIP_COUNTY_062024.csv'

# List of CSV files to combine
csv_files = [
    # 'DAC_NationalDownloadableFile_cleaned.csv',
    'HH_Provider_Jul2024_cleaned.csv',
    'Hospice_Provider_Aug2024_cleaned.csv',
    'Hospital_General_Information_cleaned.csv',
    'NH_ProviderInfo_Aug2024_cleaned.csv'
]

# Define column mappings for each data type
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

# Read FIPS and ZIP-County data
fips_df = pd.read_csv(fips_file)
fips_df.columns = fips_df.columns.str.strip()  # Strip whitespace from column names
zip_county_df = pd.read_csv(zip_county_file, dtype={'COUNTY': str, 'ZIP': str})

# Format FIPS and ZIP-County data
fips_df['fips_code'] = fips_df['FIPS State'].astype(str).str.zfill(2) + fips_df['FIPS County'].astype(str).str.zfill(3)
zip_county_df['county'] = zip_county_df['COUNTY'].str.zfill(5)

# Create final ZIP-County lookup
zip_county_final = pd.merge(
    zip_county_df[['ZIP', 'county']],
    fips_df[['fips_code', 'County Name']],
    left_on='county', right_on='fips_code',
    how='left'
)

# Read CMS data files
dataframes = []
for file in csv_files:
    file_path = os.path.join(input_dir, file)
    df = pd.read_csv(file_path, dtype={'NPI': str, 'Zip': str})
    
    # Get file type
    file_type = file.split('_cleaned.csv')[0].split('_')[0]
    file_type_mapping = {
        'NH': 'NH_ProviderInfo',
        'Hospital': 'Hospital_General_Information',
        # 'DAC': 'DAC_NationalDownloadableFile',  # Commented out to skip DAC files
        'HH': 'HH_Provider',
        'Hospice': 'Hospice_Provider'
    }
    file_type = file_type_mapping.get(file_type, file_type)

    # Skip DAC_NationalDownloadableFile_cleaned
    # if file_type == 'DAC_NationalDownloadableFile':
    #     continue  # Skip this file

    # Combine Provider_Address into Address for all file types
    if 'Provider_Address' in df.columns:
        df['Address'] = df['Provider_Address']
        df = df.drop('Provider_Address', axis=1)
    elif 'Provider Address' in df.columns:
        df['Address'] = df['Provider Address']
        df = df.drop('Provider Address', axis=1)
    
    # Rename columns based on the mapping
    df = df.rename(columns=column_mappings[file_type])
    
    # Consolidate Facility/Provider Name into Facility_Name
    df['Facility_Name'] = df.apply(
        lambda row: row['Provider_Name'] if row['Type_1'] in ['CMS - Nursing Home', 'CMS - Home Health'] else row['Facility_Name'],
        axis=1
    )
    
    # Drop unnecessary columns
    df = df.drop(columns=['CCN', 'DTC', 'Location', 'Latitude', 'Longitude'], errors='ignore')
    
    # Merge with ZIP-County data
    df = pd.merge(df, zip_county_final[['ZIP', 'County Name']], left_on='Zip', right_on='ZIP', how='left')
    
    dataframes.append(df)

# Combine all dataframes
combined_df = pd.concat(dataframes, ignore_index=True)

# Remove duplicates
combined_df = combined_df.drop_duplicates()

# Ensure 'City_Town', 'State', and 'Zip' columns are present
required_columns = ['City_Town', 'State', 'Zip']
for col in required_columns:
    if col not in combined_df.columns:
        print(f"Warning: '{col}' column is missing from the combined data.")

# Convert Zip to string and keep only the first 5 digits
combined_df['Zip'] = combined_df['Zip'].astype(str).str[:5]

# Drop the 'Provider_Name' column
combined_df = combined_df.drop(columns=['Provider_Name'], errors='ignore')
combined_df = combined_df.drop(columns=['ZIP'], errors='ignore')

# Drop the 'County' column if it exists (if not needed)
combined_df = combined_df.drop(columns=['County'], errors='ignore')

# Rename 'County_Name' to 'County' and make values uppercase
combined_df = combined_df.rename(columns={'County Name': 'County'})
combined_df['County'] = combined_df['County'].str.upper()
print(combined_df.head(10))

subset_df = combined_df.groupby('Type_1').first().reset_index()

# Save the subset DataFrame to a new CSV file
subset_output_file = output_file.replace('.csv', '_subset.csv')
subset_df.to_csv(subset_output_file, index=False)

print(f"Number of rows in combined_df: {len(combined_df)}")

# Save combined data
combined_df.to_csv(output_file, index=False)

# Output info
print(f"Combined data saved to {output_file}")
print(f"Total number of rows in combined data: {len(combined_df)}")