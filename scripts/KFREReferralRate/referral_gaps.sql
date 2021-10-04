/* SQL Query to determine proportion of patients receiving Nephrology specialty care across KFRE levels*/ 

--subquery that identifies all patients who have a history of dialysis or kidney transplant
WITH Dialysis_Patients as 
(
SELECT distinct enc.anon_id, dx_name, dx_id
FROM
  `shc_core.encounter` as enc 
    JOIN `shc_core.diagnosis_code` as dc on (pat_enc_csn_id_coded=pat_enc_csn_id_jittered)
where 
  UPPER(dc.dx_name ) like '%DIALYSIS%' OR
  (UPPER(dc.dx_name) like '%TRANSPLANT%' and UPPER(dc.dx_name) like '%KIDNEY%')
),

--subquery that queries database to only include patients that do not have a history of dialysis and/or kidney transplant. This list of patients is then used for further queries.
Excluding_Dialysis as
(
SELECT distinct enc.anon_id, 
FROM `shc_core.encounter` as enc 
  LEFT OUTER JOIN Dialysis_Patients as dial USING(ANON_ID)
WHERE 
  dial.anon_id is null 
),


-- Subquery that finds all patients with no history of dialysis/ kidney transplant that received an albumin to creatinine ratio lab result in the outpatient setting
AlbuminLabs as 
(
  SELECT 
    dem.ANON_ID, 
    DATE_DIFF(DATE(labs.result_time), dem.BIRTH_DATE_JITTERED  , YEAR) as AgeYears, 
    dem.GENDER,
    dem.CANONICAL_RACE,
    dem.INSURANCE_PAYOR_NAME,
    labs.proc_code,
    labs.group_lab_name, 
    labs.result_time , 
    labs.pat_enc_csn_id_coded,
    max(labs.ord_num_value) as MaxAlbValue, --there are sometimes multiple Alb to Creatinine ratios during an encounter so this selects for maximum within an encounter
    labs.order_id_coded, 
  EXTRACT (YEAR from labs.result_time) as Year,
  FROM 
  Excluding_Dialysis 
    JOIN 
    `shc_core.demographic` as dem USING(ANON_ID)
      JOIN `shc_core.lab_result` as labs on dem.ANON_ID=labs.anon_id 
  WHERE 
    labs.proc_code='LABUALB' and 
    labs.ordering_mode='Outpatient' and 
    (DATE_DIFF(DATE(dem.DEATH_DATE_JITTERED ), DATE(labs.result_time), DAY) >365 or dem.DEATH_DATE_JITTERED is NULL) and -- selecting for patients that are alive 1 year post ACR lab result
    labs.ord_num_value !=9999999 and labs.ord_num_value>0 and 
    EXTRACT(year from labs.result_time)>2014 and EXTRACT(year from labs.result_time)<2020
  GROUP by
  ANON_ID, result_time, dem.BIRTH_DATE_JITTERED , dem.GENDER , dem.CANONICAL_RACE , dem.INSURANCE_PAYOR_NAME , labs.proc_code , labs.group_lab_name , 
  labs.pat_enc_csn_id_coded , labs.order_id_coded 
),

-- subquery that finds all GFR labs; also converts GFR values based on race 
GFRlabs AS 

(
SELECT 
  dem.ANON_ID, 
  DATE_DIFF(DATE(labs.result_time), dem.BIRTH_DATE_JITTERED, YEAR) as AgeYears, 
  dem.GENDER, 
  labs.proc_code, 
  labs.base_name , 
  labs.result_time, 
  labs.order_id_coded,
  labs.pat_enc_csn_id_coded,
  (case when canonical_race='Black' and lab_name='GFR' THEN ord_num_value*1.21  -- when race is 'Black' and lab_name is 'GFR' multiplies by 1.21 to get MDRD Study GFR equation of African Americans
        when canonical_race!='Black' and lab_name like '%eGFR for African American%' THEN ord_num_Value/1.21 -- when race is not 'Black' but lab_name is 'eGFR for African American', divides by 1.21 to calculate 'GFR'
        else ord_num_value END) as ord_num_value, -- 'For instances when race is 'Black' and lab_name is 'eGFR for African American' the original ord_num_value is kept. When race is not 'Black' and lab_name is 'GFR' the original ord_num_value is kept
  
FROM 
  `shc_core.demographic` as dem
  JOIN `shc_core.lab_result`  as labs on dem.ANON_ID = labs.anon_id

WHERE 
  UPPER(labs.base_name) LIKE '%GFR%' AND 
  ordering_mode='Outpatient' AND
  ord_num_value <10000 AND
  ord_num_value>0 AND 
  ord_num_value is not null
), 

--subquery that finds all patients that received albumin to creatinine ratio and eGFR within 90 days of each other (indicating that they have a calculable KFRE)
GFR_ALB_JOIN AS 
(
SELECT 
  DISTINCT alb.ANON_ID , 
  alb.gender, 
  alb.AgeYears , 
  alb.pat_enc_csn_id_coded , 
  alb.order_id_coded,
  MIN(alb.result_time) as result_time, 
  alb.MaxAlbValue, 
  min(gfr.ord_num_value) as MinGFRvalue, --for when there are multiple GFR values within 90 days of ACR, selects the minimum GFR
  CASE WHEN alb.gender ='Male' then 1 else 0 end AS male, 
  
FROM 
  Albuminlabs as alb
  JOIN GFRlabs as gfr 
    USING(ANON_ID)
WHERE 
  (DATE_DIFF(DATE(alb.result_time), DATE(gfr.result_time), DAY) <90 and DATE_DIFF(DATE(alb.result_time), DATE(gfr.result_time), DAY) >-90) AND
    gfr.ord_num_value < 10000 AND --excludes lab results that are recorded in the EHR as 99999
    alb.MaxAlbValue  < 10000 
    
GROUP BY 
  ANON_ID, 
  alb.GENDER , 
  alb.AgeYears , 
  alb.result_time , 
  alb.MaxAlbValue , 
  alb.order_id_coded , 
  alb.pat_enc_csn_id_coded 
),

--subquery that calculates the KFRE betacoefficient based on the Age, Sex, GFR, and ACR
Betacoeff AS 
(
SELECT
  *,
(0.2694*0.56422)+(-0.2167*7.0355)+(-0.55418*7.2216)+(0.45608*5.2774) as beta_X_bar_Sum, --creates a new column that takes the sum of beta coefficients of each variable multiplied by the average value for each risk factor
(0.2694*MALE)+(-0.2167*AgeYears/10)+(-0.55418*MinGFRValue/5)+(0.45608*LN(GFR_ALB_JOIN.MaxAlbValue )) as beta_X_Sum -- takes the sum of beta coefficients of each risk factor multiplied the individual patient values for each risk factor (Age is divided by 10, GFR is divided by 5, natural log of ACR is taken)

FROM GFR_ALB_JOIN 
), 

--subquery that determines KFRE score based on betacoefficient
KFREScore As 
(
SELECT
  ANON_ID, Betacoeff.pat_enc_csn_id_coded,order_id_coded, result_time,gender, AgeYears, Betacoeff.MaxAlbValue , MinGFRvalue,male, 
  1-POWER(0.924,EXP(beta_x_sum - beta_x_bar_sum)) as KFRE_Score

FROM Betacoeff
),

--subquery that looks at all encounters within 1 year of date from albumin to creatinine ratio used for KFRE calculation, and determines which KFRE encounters had a follow-up encounter in Nephrology.
NephrologyConsultin1yr as 

(
SELECT kfre.*,enc.appt_when_jittered , dep.specialty, DATETIME_DIFF(enc.appt_when_jittered, kfre.result_time, DAY) as TimeLag,
CASE WHEN dep.specialty='Nephrology' then kfre.order_id_coded end as Matching_order_id_coded -- For KFRE encounters that have been seen by nephrology specialty care within +/- 1 year, 

FROM KFREScore as kfre
  JOIN `shc_core.encounter` as enc USING(ANON_ID)
    JOIN `shc_core.dep_map` as dep USING(department_id)

WHERE
  (DATETIME_DIFF(enc.appt_when_jittered, kfre.result_time, DAY)<365 and DATETIME_DIFF(enc.appt_when_jittered, kfre.result_time, DAY)>-365)
  AND dep.specialty='Nephrology'
  
),

--subquery that combines the 'KFREScore' subquery with the 'NephrologyConsultin1yr' subquery to determine which KFRE encounters received a nephrology consult within +/-1 year of calculable KFRE
--when specialty column is 'Nephrology', this indicates that KFRE encounter received nephrology care within 1 year. when specialty column is 'null', this indicates that KFRE encounter did not receive nephrology specialty care within 1 year of calculable KFRE. 
Calculable_KFRE_Left_Joined_With_Nephrology_Referral as 
(
SELECT kfre.*,
neph.appt_when_jittered , 
neph.specialty, neph.Matching_order_id_coded
FROM KFREScore as kfre 
  LEFT JOIN NephrologyConsultin1yr as neph on (kfre.order_id_coded=neph.Matching_order_id_coded)                               
),

--subquery that assigns all KFRE scores a KFRE Risk Category in 0.02 increments (i.e. all KFRE encounters between 0 and 0.02 will be assigned KFRE Risk Category of 0; all KFRE encounters between 0.02 and 0.04 will be assigned KFRE risk category of 0.02 etc)
Referral_Status as 
(

SELECT 
  *, EXTRACT (YEAR from result_time) as Year, 
  case     
    when (KFRE_Score>=0 and KFRE_Score<=0.02) then 0.00
    when (KFRE_Score>0.02 and KFRE_Score<=0.04) then 0.02
    when (KFRE_Score>0.04 and KFRE_Score<=0.06) then 0.04
    when (KFRE_Score>0.06 and KFRE_Score<=0.08) then 0.06
    when (KFRE_Score>0.08 and KFRE_Score<=0.10) then 0.08
    when (KFRE_Score>0.10 and KFRE_Score<=0.12) then 0.10
    
    when (KFRE_Score>0.12 and KFRE_Score<=0.14) then 0.12
    when (KFRE_Score>0.14 and KFRE_Score<=0.16) then 0.14
    when (KFRE_Score>0.16 and KFRE_Score<=0.18) then 0.16
    when (KFRE_Score>0.18 and KFRE_Score<=0.20) then 0.18
    when (KFRE_Score>0.20 and KFRE_Score<=0.22) then 0.20
    
    when (KFRE_Score>0.22 and KFRE_Score<=0.24) then 0.22
    when (KFRE_Score>0.24 and KFRE_Score<=0.26) then 0.24
    when (KFRE_Score>0.26 and KFRE_Score<=0.28) then 0.26
    when (KFRE_Score>0.28 and KFRE_Score<=0.30) then 0.28
    when (KFRE_Score>0.30 and KFRE_Score<=0.32) then 0.30
    
    when (KFRE_Score>0.32 and KFRE_Score<=0.34) then 0.32
    when (KFRE_Score>0.34 and KFRE_Score<=0.36) then 0.34
    when (KFRE_Score>0.36 and KFRE_Score<=0.38) then 0.36
    when (KFRE_Score>0.38 and KFRE_Score<=0.40) then 0.38
    when (KFRE_Score>0.40 and KFRE_Score<=0.42) then 0.40
    
    when (KFRE_Score>0.42 and KFRE_Score<=0.44) then 0.42
    when (KFRE_Score>0.44 and KFRE_Score<=0.46) then 0.44
    when (KFRE_Score>0.46 and KFRE_Score<=0.48) then 0.46
    when (KFRE_Score>0.48 and KFRE_Score<=0.50) then 0.48
    when (KFRE_Score>0.50 and KFRE_Score<=0.52) then 0.50
    
    when (KFRE_Score>0.52 and KFRE_Score<=0.54) then 0.52
    when (KFRE_Score>0.54 and KFRE_Score<=0.56) then 0.54
    when (KFRE_Score>0.56 and KFRE_Score<=0.58) then 0.56
    when (KFRE_Score>0.58 and KFRE_Score<=0.60) then 0.58
    when (KFRE_Score>0.60 and KFRE_Score<=0.62) then 0.60
    
    when (KFRE_Score>0.62 and KFRE_Score<=0.64) then 0.62
    when (KFRE_Score>0.64 and KFRE_Score<=0.66) then 0.64
    when (KFRE_Score>0.66 and KFRE_Score<=0.68) then 0.66
    when (KFRE_Score>0.68 and KFRE_Score<=0.70) then 0.68
    when (KFRE_Score>0.70 and KFRE_Score<=0.72) then 0.70
    
    when (KFRE_Score>0.72 and KFRE_Score<=0.74) then 0.72
    when (KFRE_Score>0.74 and KFRE_Score<=0.76) then 0.74
    when (KFRE_Score>0.76 and KFRE_Score<=0.78) then 0.76
    when (KFRE_Score>0.78 and KFRE_Score<=0.80) then 0.78
    when (KFRE_Score>0.80 and KFRE_Score<=0.82) then 0.80
    
    when (KFRE_Score>0.82 and KFRE_Score<=0.84) then 0.82
    when (KFRE_Score>0.84 and KFRE_Score<=0.86) then 0.84
    when (KFRE_Score>0.86 and KFRE_Score<=0.88) then 0.86
    when (KFRE_Score>0.88 and KFRE_Score<=0.90) then 0.88
    when (KFRE_Score>0.90 and KFRE_Score<=0.92) then 0.90
    
    when (KFRE_Score>0.92 and KFRE_Score<=0.94) then 0.92
    when (KFRE_Score>0.94 and KFRE_Score<=0.96) then 0.94
    when (KFRE_Score>0.96 and KFRE_Score<=0.98) then 0.96
    when (KFRE_Score>0.98 ) then 0.98
    end as KFRE_Risk_Category,
  case 
    when specialty is null then 0 
    when specialty='Nephrology' then 1
      end as Neph_Referral_Status --for each calculable KFRE encounter, determines if an additional nephrology specialty encounter occurred within 1 year
from Calculable_KFRE_Left_Joined_With_Nephrology_Referral
where
((DATETIME_DIFF(appt_when_jittered, result_time, DAY)<365 and appt_when_jittered>result_time) 
or appt_when_jittered is null)  
order by appt_when_jittered desc, Neph_Referral_Status desc
),

Referral_Status_by_Risk_Category as
(
SELECT 
  distinct pat_enc_csn_id_coded ,ANON_ID, 
  KFRE_Risk_Category, Year,  
  max(Neph_Referral_Status) as Received_Nephrology_Referral 
                      --each KFRE encounter will have either a '0' or '1' in the 'Neph_Referral_Status' column depending on whether or not a nephrology encounter occured within 1 year of KFRE encounter
                      --some KFRE encounters may have multiple Nephrology encounters within 1 year while others will have 0
                      --the 'max()' function is used here to indicate that if the KFRE encounter has atleast 1 nephrology encounter within 1 year, they are classified as receiving a nephrology referral.
                      --those KFRE encounters that did have atleast one nephrology encounter within 1 year will be given a '1' in the 'Received_Nephrology_Referral' column, and those without will be given a '0' 
FROM 
  Referral_Status 
Group by
  pat_enc_csn_id_coded , KFRE_Risk_Category, ANON_ID, Year
  
)

--Final query that counts distinct patient encounters at each Kidney Failure Risk level and sums the 'Received_Nephrology_Referral' from previous subquery for each Kidney Failure Risk Level
SELECT KFRE_Risk_Category as Kidney_Failure_Risk, 
  COUNT(distinct pat_enc_csn_id_coded ) as nEncounters, 
  SUM(Received_Nephrology_Referral) as Total_Nephrology_Referrals, 
  ROUND(SUM(Received_Nephrology_Referral)/COUNT(distinct pat_enc_csn_id_coded ), 3) as Proportion_Of_Nephrology_Referral,
FROM Referral_Status_by_Risk_Category 
WHERE
  Year>2014 and Year<2020
GROUP By
  KFRE_Risk_Category 
Order by  
  KFRE_Risk_Category asc, 
  nEncounters desc