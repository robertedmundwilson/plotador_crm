# crm_app/data/scripts/combines_all.py

import pandas as pd

# Load the first CSV
df1 = pd.read_csv('/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/Admin_raw.csv')

# Load the second CSV and perform a left join
df2 = pd.read_csv('/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/HCHB_cleaned_lat_long.csv')
combined_df = df1.merge(df2[['addr_full', 'Latitude', 'Longitude', 'geo_lat_long']], on='addr_full', how='left')

# Save the final DataFrame to a CSV file
combined_df.to_csv('/Users/robertwilson/CMS_Datafiles/Sept_2024/CMS_cleaned/totes_combo.csv', index=False)
