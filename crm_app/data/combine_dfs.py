import pandas as pd
import os

# Purpose: Clean data so one row per mappable unit. For example, there should only be one row per clinician.

# Determine the path to the CSV file
current_directory = os.path.dirname(__file__)

doc_clinicians_CSV_FILE = os.path.join(current_directory, 'doc_clinicians_SC_enhanced.csv')
home_CSV_FILE = os.path.join(current_directory, 'home_july7_enhanced.csv')
hospice_CSV_FILE = os.path.join(current_directory, 'hospice_july7_enhanced.csv')
hospital_CSV_FILE = os.path.join(current_directory, 'hospital_july7_enhanced.csv')
provider_CSV_FILE = os.path.join(current_directory, 'provider_july7_enhanced.csv')


# Read the CSV file into a DataFrame
doc_clinicians_df = pd.read_csv(doc_clinicians_CSV_FILE)
home_df = pd.read_csv(home_CSV_FILE)
hospice_df = pd.read_csv(hospice_CSV_FILE)
hospital_df = pd.read_csv(hospital_CSV_FILE)
provider_df = pd.read_csv(provider_CSV_FILE)

### Clinicians
#unique row identifer: 'NPI'
clinicians_short_df = doc_clinicians_df.copy()  # Make a copy to avoid modifying the original DataFrame
clinicians_short_df['data_source'] = 'clinicians'
clinicians_short_df['key_id'] = clinicians_short_df['NPI']
# Combine 'Provider Last Name' and 'Provider First Name' into 'name_full'
clinicians_short_df['name_full'] = clinicians_short_df['Provider Last Name'] + ', ' + clinicians_short_df['Provider First Name']
# Count non-null values in 'adr_ln_1', 'adr_ln_2', 'Telephone Number' for each row
clinicians_short_df['non_null_count'] = clinicians_short_df[['adr_ln_1', 'adr_ln_2', 'Telephone Number']].count(axis=1)

# Count occurrences of 'adr_ln_1' + 'adr_ln_2' combinations
clinicians_short_df['address_count'] = clinicians_short_df.groupby(['adr_ln_1', 'adr_ln_2'])['NPI'].transform('count')

# Sort by the criteria: least nulls, highest address count, and keep the first row in case of ties
clinicians_selected_df = (
    clinicians_short_df.sort_values(
        by=['non_null_count', 'address_count'],
        ascending=[True, False]
    )
    .groupby('NPI', as_index=False)
    .first()
)

# Selecting the specified columns
selected_cols = [
    'data_source', 'key_id', 'name_full', 'NPI', 'Cred', 'Med_sch', 'Grd_yr', 'pri_spec',
    'sec_spec_all', 'Facility Name', 'adr_ln_1', 'adr_ln_2', 'City/Town',
    'State', 'ZIP Code', 'Telephone Number', 'Cleaned Address', 'Latitude', 'Longitude'
]
clinicians_selected_df = clinicians_selected_df[selected_cols]

### Clinician Network
#unique row identifer: 'org_pac_id'
clinician_network_df = doc_clinicians_df.copy()  # Make a copy to avoid modifying the original DataFrame
clinician_network_df['data_source'] = 'clinician_network'
clinician_network_df['key_id'] = clinician_network_df['org_pac_id']

# Combine 'Provider Last Name' and 'Provider First Name' into 'name_full'
clinician_network_df['name_full'] = clinician_network_df['Facility Name']

# Count distinct NPIs for each org_pac_id
clinician_network_df['distinct_npi_count'] = clinician_network_df.groupby('org_pac_id')['NPI'].transform('nunique')

# Count occurrences of 'adr_ln_1' + 'adr_ln_2' combinations
clinician_network_df['adr_ln_2'] = clinician_network_df['adr_ln_2'].fillna('')
clinician_network_df['address_count'] = clinician_network_df.groupby(['adr_ln_1', 'adr_ln_2'])['org_pac_id'].transform('count')

# Sort by the criteria: distinct_npi_count, address_count, and keep the first row in case of ties
clinician_network_df_sorted = (
    clinician_network_df.sort_values(
        by=['distinct_npi_count', 'address_count'],
        ascending=[False, False]
    )
    .groupby('org_pac_id', as_index=False)
    .first()
)

# Selecting the specified columns
selected_cols = [
    'data_source', 'key_id', 'name_full', 'org_pac_id', 'num_org_mem', 'pri_spec',
    'sec_spec_all', 'adr_ln_1', 'adr_ln_2', 'City/Town',
    'State', 'ZIP Code', 'Telephone Number', 'Cleaned Address', 'Latitude', 'Longitude',
]
clinician_network_df_final = clinician_network_df_sorted[selected_cols]


### Home Health
#unique row identifer: 'CMS Certification Number (CCN)'
home_short_df = home_df.copy()  # Make a copy to avoid modifying the original DataFrame
home_short_df['data_source'] = 'home_health_agencies'
home_short_df['key_id'] = home_short_df['CMS Certification Number (CCN)']

# Combine 'Provider Last Name' and 'Provider First Name' into 'name_full'
home_short_df['name_full'] = home_short_df['Provider Name']
home_short_df.rename(columns={'CMS Certification Number (CCN)': 'CMS_CNN'}, inplace=True)


### Hospice Health
#unique row identifer: 'CMS_CNN'
hospice_short_df = hospice_df.copy()
# Assign 'data_source' and combine 'Provider Last Name' and 'Provider First Name' into 'name_full'
hospice_short_df['data_source'] = 'hospice_providers'
hospice_short_df['key_id'] = hospice_short_df['CMS Certification Number (CCN)']
hospice_short_df['name_full'] = hospice_short_df['Facility Name']
# Rename 'CMS Certification Number (CCN)' to 'CMS_CNN' if it exists
# if 'CMS Certification Number (CCN)' in hospice_df.columns:
hospice_short_df.rename(columns={'CMS Certification Number (CCN)': 'CMS_CNN'}, inplace=True)
# Ensure columns exist
# if 'Measure Name' in hospice_df.columns and 'Score' in hospice_df.columns:
    # Select rows where Measure Name is 'Average Daily Census' to get corresponding Score
average_daily_census_scores = hospice_short_df[hospice_short_df['Measure Name'] == 'Average Daily Census'][['CMS_CNN', 'Score']]
# Remove duplicates by keeping the first occurrence of each 'CMS_CNN'
average_daily_census_scores = average_daily_census_scores.drop_duplicates(subset=['CMS_CNN'], keep='first')
# Merge to combine scores with hospice_df
hospice_short_df = hospice_short_df.merge(average_daily_census_scores, on='CMS_CNN', how='left', suffixes=('', '_Average_Daily_Census'))
# Keep selected columns and rename 'Score' column to 'Average_Daily_Census'
selected_cols = ['data_source', 'key_id', 'CMS_CNN', 'name_full', 'Facility Name', 'Address Line 1', 'Address Line 2', 'City/Town', 'State',
                 'ZIP Code', 'County/Parish', 'Telephone Number', 'CMS Region', 'Score_Average_Daily_Census', 'Cleaned Address', 'Latitude', 'Longitude']
hospice_short_df = hospice_short_df[selected_cols].rename(columns={'Score_Average_Daily_Census': 'Average_Daily_Census'})
# Drop duplicate rows for the same CMS_CNN
hospice_short_df.drop_duplicates(subset='CMS_CNN', keep='first', inplace=True)


### Hospital
#unique row identifer: 'Facility ID'
hospital_short_df = hospital_df.copy()  # Make a copy to avoid modifying the original DataFrame
hospital_short_df['data_source'] = 'hospital'
hospital_short_df['key_id'] = hospital_short_df['Facility ID']

# Combine 'Provider Last Name' and 'Provider First Name' into 'name_full'
hospital_short_df['name_full'] = hospital_short_df['Facility Name']

### Provider (Nursing Homes)
provider_short_df = provider_df.copy()  # Make a copy to avoid modifying the original DataFrame
provider_short_df['data_source'] = 'nursing_home'
# Combine 'Provider Last Name' and 'Provider First Name' into 'name_full'
provider_short_df['name_full'] = provider_short_df['Provider Name']


### Generate and save csvs for each flattened df
clinicians_cleaned_df = os.path.join(current_directory, 'clinicians_cleaned_df.csv')
clinicians_selected_df.to_csv(clinicians_cleaned_df, index=False)

clinician_network_cleaned_df = os.path.join(current_directory, 'clinician_network_cleaned_df.csv')
clinician_network_df_final.to_csv(clinician_network_cleaned_df, index=False)

home_cleaned_df = os.path.join(current_directory, 'home_cleaned_df.csv')
home_short_df.to_csv(home_cleaned_df, index=False)

hospice_cleaned_df = os.path.join(current_directory, 'hospice_cleaned_df.csv')
hospice_short_df.to_csv(hospice_cleaned_df, index=False)

hospital_cleaned_df = os.path.join(current_directory, 'hospital_cleaned_df.csv')
hospital_short_df.to_csv(hospital_cleaned_df, index=False)

provider_cleaned_df = os.path.join(current_directory, 'provider_cleaned_df.csv')
provider_short_df.to_csv(provider_cleaned_df, index=False)


## Create combo df. This will be especially useful for mapping
clinicians_selected_df = clinicians_selected_df[['data_source', 'name_full', 'Cleaned Address', 'Latitude', 'Longitude']]
clinician_network_df_final = clinician_network_df_final[['data_source', 'name_full', 'Cleaned Address', 'Latitude', 'Longitude']]
home_short_df = home_short_df[['data_source', 'name_full', 'Cleaned Address', 'Latitude', 'Longitude']]
hospice_short_df = hospice_short_df[['data_source', 'name_full', 'Cleaned Address', 'Latitude', 'Longitude']]
hospital_short_df = hospital_short_df[['data_source', 'name_full', 'Cleaned Address', 'Latitude', 'Longitude']]
provider_short_df = provider_short_df[['data_source', 'name_full', 'Cleaned Address', 'Latitude', 'Longitude']]

# Concatenate the DataFrames together
final_df = pd.concat([
    clinicians_selected_df,
    clinician_network_df_final,
    home_short_df,
    hospice_short_df,
    hospital_short_df,
    provider_short_df
])

combo_cleaned_df = os.path.join(current_directory, 'combo_cleaned_df.csv')
final_df.to_csv(combo_cleaned_df, index=False)




