 CREATE OR REPLACE VIEW `moments-full.CMS.demo_vw` AS


 WITH county_selection AS (
  SELECT 
    b.Zip,
    b.County_Name,
    ROW_NUMBER() OVER (PARTITION BY b.Zip ORDER BY b.County_Name) AS rn
  FROM `moments-full.CMS.final_zip_county` b
)

SELECT 
  Type,
  CAST(ID_rw AS STRING) AS row_id,
  Name,
  addr_full,
  Phone,
  Admission_Coordinator,
  CAST(Calls_6months AS STRING) AS Calls_last_6_months,  -- Cast to STRING
  CAST(Referrals_6months AS STRING) AS Referrals_last_6_months,  -- Cast to STRING
  CAST(ac_active AS STRING) AS ac_active,  -- Cast to STRING
  '' AS pri_spec,
  '' AS Provider_Last,
  '' AS Provider_First,
  CAST('' AS STRING) AS Beds,  -- Ensure Beds is STRING
  City,
  State,
  CAST(a.Zip AS STRING) AS Zip,
  c.County_Name,
  geo_lat_long
FROM `moments-full.CMS.demo_accounts_lat_long_WI` a
LEFT JOIN county_selection c
ON CAST(a.Zip AS STRING) = CAST(c.Zip AS STRING)
WHERE c.rn = 1

UNION ALL 

SELECT 
  Type_1 AS Type,
  '' AS row_id,
  Facility_Name AS Name,
  Full_Address AS addr_full,
  Telephone AS Phone,
  'CMS Facility' AS Admission_Coordinator,
  '' AS Calls_last_6_months,
  '' AS Referrals_last_6_months,
  '' AS ac_active,  -- Empty string for second query
  '' AS pri_spec,
  '' AS Provider_Last,
  '' AS Provider_First,
  CAST(Beds AS STRING) AS Beds,  -- Cast Beds to STRING
  City_Town AS City,
  State,
  CAST(Zip AS STRING) AS Zip,
  County,
  geo_lat_long
FROM 
  `moments-full.CMS.demo_cms_lat_long`