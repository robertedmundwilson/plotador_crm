CREATE OR REPLACE VIEW `moments-full.CMS.FINAL_vw` AS

SELECT 
  Type,
  CAST(ID_rw AS STRING) AS row_id,
  Name,
  addr_full,
  Phone,
  Admission_Coordinator___Hospice AS Admission_Coordinator,
  CAST(Calls_last_6_months AS STRING) AS Calls_last_6_months,  -- Cast to STRING
  CAST(Referrals_last_6_months AS STRING) AS Referrals_last_6_months,  -- Cast to STRING
  CAST(ac_active AS STRING) AS ac_active,  -- Cast to STRING
  '' AS pri_spec,
  '' AS Provider_Last,
  '' AS Provider_First,
  CAST('' AS STRING) AS Beds,  -- Ensure Beds is STRING
  City,
  State,
  CAST(a.Zip AS STRING) AS Zip,
  b.County_Name
FROM `moments-full.CMS.SHORT_6` a
LEFT JOIN `moments-full.CMS.final_zip_county` b
ON CAST(a.Zip AS STRING) = CAST(b.Zip AS STRING)
WHERE Type IS NOT NULL
AND State NOT IN ('null','~','GU','MP','AS','PR','State','VI') 
AND NAME <> '*NONE'

UNION ALL 

SELECT 
  Type_1 AS Type,
  '' AS row_id,
  Facility_Name AS Name,
  Full_Address AS addr_full,
  Telephone AS Phone,
  'CMS - Unassigned' AS Admission_Coordinator,
  '' AS Calls_last_6_months,
  '' AS Referrals_last_6_months,
  '' AS ac_active,  -- Empty string for second query
  pri_spec,
  Provider_Last,
  Provider_First,
  CAST(Beds AS STRING) AS Beds, 
  City_Town AS City,
  State,
  CAST(Zip AS STRING) AS Zip,
  UPPER(County) AS County
FROM 
  `moments-full.CMS.all_cms_clean6`
WHERE State NOT IN ('null','~','GU','MP','AS','PR','State','VI')