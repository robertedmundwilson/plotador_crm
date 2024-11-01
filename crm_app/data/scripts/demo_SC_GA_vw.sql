CREATE OR REPLACE VIEW `moments-full.CMS.demo_SC_GA_vw` AS

SELECT Type_1 AS Type,
  Facility_Name AS Name,
  Cleaned_Address AS addr_full,
  Telephone AS Phone,
  '' AS Admission_Coordinator,
  -- CAST(Calls_last_6_months AS STRING) AS Calls_last_6_months,  -- Cast to STRING
  County AS County_Name,  -- Cast to STRING
  '' AS ac_active,  -- Cast to STRING
  '' AS pri_spec,
  Provider_Last,
  Provider_First,
  Potential,  -- Ensure Beds is STRING
  City_Town AS City,
  State,
  CAST(Zip AS STRING) AS Zip,  -- Cast Zip to STRING
  NPI,
  geo_lat_long
FROM `moments-full.CMS.demo_SC_GA`


