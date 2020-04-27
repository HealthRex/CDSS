-- Draft queries of STARR-OMOP database to pull out number of 
--  co-tests for SARS-CoV2 and other viruses, and how often see (co)infections with each

/*
select *
from `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` as measConc
where concept_id IN (706170)
*/
With
sarscov2meas AS
(
  SELECT *
  FROM
  `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.measurement` as meas
  WHERE
      measurement_concept_id IN (706170) -- SARS-Cov2-NAA
      and value_source_value is not null
      and meas.measurement_DATE >= '2020-02-01'
),
anySameDayVirusMeas AS
(
  SELECT meas.measurement_id, meas.person_id, meas.measurement_concept_id, measConc.concept_name, meas.measurement_DATE, meas.measurement_datetime, 
         meas.value_source_value in ('Detected','Pos','Positive') as virusDetected, 
         sarscov2meas.value_source_value in ('Detected','Pos','Positive') as sarscov2Detected, 
         count(*)
  FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.measurement` as meas
     join `som-rit-phi-starr-prod.starr_omop_cdm5_deid_latest.concept` as measConc ON (meas.measurement_concept_id = measConc.concept_id )
     join sarscov2meas on meas.person_id = sarscov2meas.person_id and meas.measurement_DATE = sarscov2meas.measurement_DATE 
  WHERE 
     lower(measConc.concept_name) like '%naa with probe detection%'
     and meas.measurement_concept_id <> 706170
     and meas.value_source_value is not null
  GROUP BY meas.measurement_id, meas.person_id, meas.measurement_concept_id, measConc.concept_name, meas.measurement_DATE, meas.measurement_datetime, meas.value_source_value, sarscov2meas.value_source_value 
  ORDER BY meas.person_id, meas.measurement_DATETIME desc
),
virusDetectedCounts AS
(
  select person_id, measurement_date, countif(virusDetected) > 0 as anyOtherVirusDetected, sarscov2Detected 
  from anySameDayVirusMeas 
  group by person_id, measurement_DATE, sarscov2Detected 
)
select 
   count(sarscov2Detected) as nCoTests,
   countif(anyOtherVirusDetected) as nAnyOtherVirus,
   countif(sarscov2Detected) as nSARSCoV2,
   countif(anyOtherVirusDetected and sarscov2Detected) as nCoinfection
from virusDetectedCounts 
limit 100

/*
SELECT value_source_value, count(*)
from anySameDayVirusMeas 
group by value_source_value 
order by count(*) desc

--('Detected','Pos','Positive')

limit 100
*/


