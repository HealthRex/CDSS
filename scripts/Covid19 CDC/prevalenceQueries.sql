WITH

-- Collate patients receiving any recent acute respiratory illness (ARI) diagnosis
recentARI AS
( -- Look for any patient with an ARI, based on diagnosis code list suggested by CDC,
  --  that was recorded recently (since 12/2019).
  SELECT
    person_id, visit_occurrence_id, condition_start_DATE, condition_start_DATETIME, 
    condition_source_value, condition_source_concept_id
  FROM
    `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.condition_occurrence` AS condOccur 
  WHERE
    condition_start_DATE >= '2019-12-01' AND
    ( condition_source_value LIKE 'J00.%' OR
      condition_source_value LIKE 'J01.%' OR
      condition_source_value LIKE 'J02.%' OR
      condition_source_value LIKE 'J03.%' OR
      condition_source_value LIKE 'J04.%' OR
      condition_source_value LIKE 'J05.%' OR
      condition_source_value LIKE 'J06.%' OR
      condition_source_value LIKE 'J09.%' OR
      condition_source_value LIKE 'J10.%' OR
      condition_source_value LIKE 'J11.%' OR
      condition_source_value LIKE 'J12.%' OR
      condition_source_value LIKE 'J13.%' OR
      condition_source_value LIKE 'J14.%' OR
      condition_source_value LIKE 'J15.%' OR
      condition_source_value LIKE 'J16.%' OR
      condition_source_value LIKE 'J17.%' OR
      condition_source_value LIKE 'J18.%' OR
      condition_source_value LIKE 'J20.%' OR
      condition_source_value LIKE 'J21.%' OR
      condition_source_value LIKE 'J22' OR
      condition_source_value LIKE 'J80' OR
      condition_source_value LIKE 'A37.91' OR
      condition_source_value LIKE 'A37.01' OR
      condition_source_value LIKE 'A37.11' OR
      condition_source_value LIKE 'A37.81' OR
      condition_source_value LIKE 'A48.1' OR
      condition_source_value LIKE 'B25.0' OR
      condition_source_value LIKE 'B44.0' OR
      condition_source_value LIKE 'B97.4' OR
      condition_source_value LIKE 'U07.1'
    )
),
recentARIDateTimeRange AS
( -- Look for only the last / most recent ARI occurrence date for each patient, in case one has multiple
  SELECT
    recentARI.person_id,
    MIN(condition_start_DATETIME) AS firstARIDateTime, MAX(condition_start_DATETIME) AS lastARIDateTime
  FROM recentARI
  GROUP BY recentARI.person_id 
),


-- Collate results on anyone receiving the SARS-CoV2 NAA Test Results
resultsSARSCoV2Tests AS
(
  SELECT person_id, visit_occurrence_id, measurement_DATE, measurement_DATETIME, value_source_value, value_source_value IN ('Detected','Pos','Positive') AS detectedSARSCoV2
  FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.measurement` as meas
  WHERE measurement_concept_id = 706170 -- SARS-CoV2 NAA Test Result
  AND meas.value_source_value is NOT NULL -- Only capture usable results and not extra descriptors
) ,
/* Note how often get null values
select count(*) nRecords, count(distinct person_id) as nPerson, count(distinct visit_occurrence_id) as nVisits, countif(value_source_value is not null) as nonNullValues
from resultsSARSCoV2Tests 

nRecords  42268
nPerson 14934
nVisits 21043
nonNullValues 21197
*/  
resultsSARSCoV2DateTimeRange AS
( -- Accounting for multiple possible tests per patient, group by patient ID and collate date time ranges
  SELECT 
    person_id, 
    firstSARSCoV2TestedDateTime, lastSARSCoV2TestedDateTime,
    firstSARSCoV2DetectedDateTime, lastSARSCoV2DetectedDateTime 
  FROM
  (
    SELECT person_id, MIN(measurement_DATETIME) AS firstSARSCoV2TestedDateTime, MAX(measurement_DATETIME) AS lastSARSCoV2TestedDateTime
    FROM resultsSARSCoV2Tests
    GROUP BY person_id 
  ) AS firstLastSARSCoV2Tests
  LEFT JOIN -- Left outer join, because not everyone who had a test will have a positive test result to join to
  (
    SELECT person_id, MIN(measurement_DATETIME) AS firstSARSCoV2DetectedDateTime, MAX(measurement_DATETIME) AS lastSARSCoV2DetectedDateTime
    FROM resultsSARSCoV2Tests
    WHERE resultsSARSCoV2Tests.detectedSARSCoV2
    GROUP BY person_id 
  ) AS firstLastDetectedSARSCoV2Tests
  USING (person_id)
),

-- At this point:
--  recentARIDateTimeRange has one row per patient (41,341 rows as of 2020-04-20 cdm_release_DATE)
--  resultsSARSCoV2DateTimeRange has one row per patient (14,838)
-- Each with first and last dates of occurrences of ARI (after initial "recent" cutoff date) orSARS-CoV2 test results (including timing of positive/detected result, null if no positive/detected results)
recentARIandSARSCoV2DateTimeRange AS
( -- Full outer join in both directions because some people with ARI diagnosis don't get SARS-CoV2 testing and vice versa
  SELECT *,
      DATETIME_DIFF( firstSARSCoV2TestedDateTime, firstARIDateTime, DAY ) daysFirstARItoFirstSARSCoV2Tested,
      DATETIME_DIFF( firstSARSCoV2TestedDateTime, lastARIDateTime, DAY ) daysLastARItoFirstSARSCoV2Tested,
      DATETIME_DIFF( lastSARSCoV2TestedDateTime, firstARIDateTime, DAY ) daysFirstARItoLastSARSCoV2Tested,
      DATETIME_DIFF( lastSARSCoV2TestedDateTime, lastARIDateTime, DAY ) daysLastARItoLastSARSCoV2Tested,

      DATETIME_DIFF( firstSARSCoV2DetectedDateTime, firstARIDateTime, DAY ) daysFirstARItoFirstSARSCoV2Detected,
      DATETIME_DIFF( firstSARSCoV2DetectedDateTime, lastARIDateTime, DAY ) daysLastARItoFirstSARSCoV2Detected,
      DATETIME_DIFF( lastSARSCoV2DetectedDateTime, firstARIDateTime, DAY ) daysFirstARItoLastSARSCoV2Detected,
      DATETIME_DIFF( lastSARSCoV2DetectedDateTime, lastARIDateTime, DAY ) daysLastARItoLastSARSCoV2Detected,
  FROM 
    recentARIDateTimeRange FULL JOIN 
    resultsSARSCoV2DateTimeRange USING (person_id)
  -- 4,091 inner join results (recent ARI diagnosis code AND SARS-CoV2 test results exist, but not necessarily in the correct datetime order)
  -- 52,088 full outer join results (recent ARI diagnosi code OR SARS-CoV2 test results)
),

recentARIandSARSCoV2DateTimeRangeWithPatientDemo AS
( -- Join patient demographic information
  SELECT 
    recentARIandSARSCoV2DateTimeRange.*,
    year_of_birth, DATE_DIFF('2020-02-01', DATE(birth_DATETIME), YEAR) ageAsOfFeb2020,
    person.gender_concept_id , genderConc.concept_name AS genderConcept,
    person.race_source_value, person.race_concept_id, raceConc.concept_name as raceConcept,
    person.ethnicity_source_value, person.ethnicity_concept_id, ethnicityConc.concept_name as ethnicityConcept
  FROM 
    recentARIandSARSCoV2DateTimeRange 
    JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.person` AS person USING (person_id) 
    LEFT JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` AS genderConc ON (person.gender_concept_id = genderConc.concept_id)
    LEFT JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` AS raceConc ON (person.race_concept_id = raceConc.concept_id)
    LEFT JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` AS ethnicityConc ON (person.ethnicity_concept_id = ethnicityConc.concept_id)
)

-- Example query for primary ARI and SARS CoV2 testing counts, grouped by different categories
SELECT
  CAST(FLOOR(ageAsOfFeb2020 / 10)*10 AS INT64) AS ageMin, CAST(FLOOR(ageAsOfFeb2020 / 10)*10+10 AS INT64) as ageMax,
  COUNTIF(lastARIDateTime IS NOT NULL) as nARIPatients,
  COUNTIF(lastSARSCoV2TestedDateTime IS NOT NULL) as nSARSCoV2TestedPatients,
  COUNTIF(lastSARSCoV2DetectedDateTime IS NOT NULL) as nSARSCoV2DetectedPatients,
  -- Looking for relative date relationship between ARI diagnosis and SARS-CoV2 Test.
  -- This logic is imperfect as is based on date spans. Consider redoing, but using patient-days as unit of observation (rows) instead of patients
  COUNTIF( daysFirstARItoFirstSARSCoV2Tested BETWEEN 0 AND 60 OR daysLastARItoFirstSARSCoV2Tested BETWEEN 0 AND 60 ) AS nARIPatientsSARSCoV2TestedWithin60Days,
  COUNTIF( daysFirstARItoFirstSARSCoV2Detected BETWEEN 0 AND 60 OR daysLastARItoFirstSARSCoV2Detected BETWEEN 0 AND 60 ) AS nARIPatientsSARSCoV2DetectedWithin60Days
FROM recentARIandSARSCoV2DateTimeRangeWithPatientDemo 
GROUP BY ageMin, ageMax
ORDER BY ageMin

LIMIT 100