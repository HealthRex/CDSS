

cohort AS
(
    SELECT * FROM selectDRGs
),

-- Goal: A) Find top diagnoses by greatest volume / tottal cost / cost variation / LOS. B) find comorbidities on admission
-- avg 24 records per encounter
-- Expect exactly 1 'primary' dx per enc, --> HOWEVER of the 12665 enc: # of 'primary' dx per encounter: (0,1,2) = (1627,11036,2)
diagnosesOnAdmission AS
(
    SELECT DISTINCT enc, admsnTimeJTR,
            icd10, dx_name, start_date, primary,
            DATETIME_DIFF(a.admsnTimeJTR, b.start_date, DAY) as daysDocumentedBeforeAdmsn,
            if(DATETIME_DIFF(b.start_date, a.admsnTimeJTR, HOUR) >= 0, 1, 0) as withinFirst24H
            # the following are almost entirely missing data: hospital_pl, problem_status, poa, present_on_adm, noted_date, hx_date_of_entry, end_date, resolved_date
            #count(case primary when 'Y' then 1 else null end) as numPrimary
            #REGEXP_EXTRACT(icd10, r'[A-Z]\d+') as icd10prefix
    FROM cohort a
    JOIN `mining-clinical-decisions.shc_core.diagnosis_code` b
    ON (a.anon_id = b.anon_id)
        AND DATETIME_DIFF(b.start_date, a.admsnTimeJTR, HOUR) <= 24 -- start_date exists for every record in ::diagnosis_code
),


icd10_matching AS
(
    -- filter out redundancies: only 1 unique ICD10 per patient encounter corresponding to its earliest documented instance
    SELECT DISTINCT enc, admsnTimeJTR, ICD10_string,
                min(start_date) as earliestNoted,
                if(DATETIME_DIFF(min(start_date), admsnTimeJTR, HOUR) >= 0, 1, 0) as withinFirst24H,
                DATETIME_DIFF(admsnTimeJTR,min(start_date),DAY) as daysFirstDocumentedBeforeAdmsn
    FROM
    (
        -- The following captures almost all ICD10s in the diagnosis_code table. Only thing left are rows with multiple ICD10's separated by commas --> small minority, excluding for now
        SELECT enc, admsnTimeJTR, start_date, ICD10_string
        FROM diagnosesOnAdmission a
        JOIN `mining-clinical-decisions.ahrq_ccsr.diagnosis_code` b
        ON a.icd10 = b.ICD10
        UNION DISTINCT
        SELECT enc, admsnTimeJTR, start_date, ICD10_string
        FROM diagnosesOnAdmission a
        JOIN `mining-clinical-decisions.ahrq_ccsr.diagnosis_code` b
        ON CONCAT(a.icd10,".") = b.ICD10
    ) x
    GROUP BY enc, admsnTimeJTR, ICD10_string
    ORDER BY enc, daysFirstDocumentedBeforeAdmsn
),

-- match to CCSR categories
icd10_CCSR AS
(
    SELECT DISTINCT enc, admsnTimeJTR, earliestNoted, withinFirst24H, daysFirstDocumentedBeforeAdmsn, b.*
    FROM icd10_matching a
    JOIN `som-nero-phi-jonc101-secure.codes.diagnoses_AHRQ_CCSR` b
    ON ICD10_string = b.ICD10
    ORDER BY enc, earliestNoted
)

SELECT * FROM icd10_CCSR
