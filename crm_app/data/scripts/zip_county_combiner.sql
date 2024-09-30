-- Step 1
CREATE OR REPLACE EXTERNAL TABLE `moments-full.CMS.fips_codes`
OPTIONS (
  format = 'CSV',
  uris = ['gs://plotador-cms-2024/US_FIPS_Codes.csv'] -- Update to your GCS URI
);

-- Step 2
CREATE OR REPLACE EXTERNAL TABLE `moments-full.CMS.zip_county`
OPTIONS (
  format = 'CSV',
  uris = ['gs://plotador-cms-2024/ZIP_COUNTY_062024.csv'] -- Update to your GCS URI
);

-- Step 3
CREATE OR REPLACE TABLE `moments-full.CMS.final_zip_county` AS
WITH fips_data AS (
  SELECT 
    LPAD(CAST(`FIPS_State` AS STRING), 2, '0') AS fips_state,
    LPAD(CAST(`FIPS_County` AS STRING), 3, '0') AS fips_county,
    `County_Name`,
    LPAD(CAST(`FIPS_State` AS STRING), 2, '0') || LPAD(CAST(`FIPS_County` AS STRING), 3, '0') AS fips_code
  FROM `moments-full.CMS.fips_codes`
),
zip_data AS (
  SELECT 
    `ZIP` AS zip,
    LPAD(CAST(`COUNTY` AS STRING), 5, '0') AS county
  FROM `moments-full.CMS.zip_county`
)
SELECT 
  z.zip,
  f.`County_Name`
FROM 
  zip_data z
LEFT JOIN 
  fips_data f ON z.county = f.fips_code
WHERE f.`County_Name` IS NOT NULL
