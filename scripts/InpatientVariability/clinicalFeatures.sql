WITH

selectDRGs AS
(
    SELECT * FROM `som-nero-phi-jonc101-secure.kush_db.selectDRGs`
),

-- determine which sub-categories of cost were (1) biggest drivers, (2) most variable
costBreakdown AS
(
    SELECT b.*
    FROM selectDRGs a
    JOIN `som-nero-phi-jonc101-secure.shc_cost.costUB` b
    ON a.mrn = b.MRN AND a.AdmitTRUE = b.AdmitDate
),

-- patient age, comorbidities, demographic
patientFactors AS
(
    SELECT ANON_ID, GENDER, CANONICAL_ETHNICITY, CANONICAL_RACE, INTRPTR_NEEDED_YN, INSURANCE_PAYOR_NAME, BMI, CHARLSON_SCORE, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL, BIRTH_DATE_JITTERED
    FROM
        (SELECT DISTINCT anon_id FROM selectDRGs) a
    JOIN `mining-clinical-decisions.shc_core.demographic`
    USING(anon_id)
),

-- collect orders (placed) for RT
respiratoryTherapy AS
(
    SELECT DISTINCT anon_id, order_proc_id_coded, pat_enc_csn_id_coded as enc, order_type, proc_id, description, display_name, authrzing_prov_id,
                    order_inst_jittered as rt_orderInstJTR, proc_start_time_jittered as rt_procStartJTR, last_stand_perf_tm_jittered as rt_procFinalJTR -- order_time_jittered redundant? seems equivalent to order_inst_jittered
    FROM `mining-clinical-decisions.shc_core.order_proc` -- other potential tables to consider: order_proc, procedure_code, proc_orderset
    WHERE (LOWER(order_class) LIKE '%hospital%' OR LOWER(order_class) LIKE '%stanford%' OR LOWER(order_class) LIKE '%point of care%' OR LOWER(order_class) LIKE '%normal%')
    AND ordering_mode = 'Inpatient'

    -- respiratory therapy
    AND proc_id IN (931,1196,1962,542,5039,1769,425922)
    AND order_type IN ('Respiratory Care') # order_type 'PFT' is unrelated to RT in my opinion
),

-- collect orders (placed) for OT
occupationalTherapy AS
(
    SELECT DISTINCT anon_id, order_proc_id_coded, pat_enc_csn_id_coded as enc, order_type, proc_id, description, display_name, authrzing_prov_id,
                    order_inst_jittered as ot_orderInstJTR, proc_start_time_jittered as ot_procStartJTR, last_stand_perf_tm_jittered as ot_procFinalJTR -- order_time_jittered redundant? seems equivalent to order_inst_jittered
    FROM `mining-clinical-decisions.shc_core.order_proc` -- other potential tables to consider: order_proc, procedure_code, proc_orderset
    WHERE (LOWER(order_class) LIKE '%hospital%' OR LOWER(order_class) LIKE '%stanford%' OR LOWER(order_class) LIKE '%point of care%' OR LOWER(order_class) LIKE '%normal%')
    AND ordering_mode = 'Inpatient'

    -- occupational therapy
    AND order_type IN ('OT','REHAB')
    AND proc_id IN (199493,1575,507087,420225,419445,17587,172763,1577,172765,399680)
),

-- collect orders (placed) for PT
physicalTherapy AS
(
    SELECT DISTINCT anon_id, order_proc_id_coded, pat_enc_csn_id_coded as enc, order_type, proc_id, description, display_name, authrzing_prov_id,
                    order_inst_jittered as pt_orderInstJTR, proc_start_time_jittered as pt_procStartJTR, last_stand_perf_tm_jittered as pt_procFinalJTR -- order_time_jittered redundant? seems equivalent to order_inst_jittered
    FROM `mining-clinical-decisions.shc_core.order_proc` -- other potential tables to consider: order_proc, procedure_code, proc_orderset
    WHERE (LOWER(order_class) LIKE '%hospital%' OR LOWER(order_class) LIKE '%stanford%' OR LOWER(order_class) LIKE '%point of care%' OR LOWER(order_class) LIKE '%normal%')
    AND ordering_mode = 'Inpatient'

    -- physical therapy
    AND order_type IN ('PT','REHAB')
    AND proc_id IN (37225,1717,175908,189238,439060,467954,420233,389602,425090,432201,219820,13123,461330,119293,13121,259884)

),

-- collect orders (placed) for ST / SLP
speechTherapy AS
(
    SELECT DISTINCT anon_id, order_proc_id_coded, pat_enc_csn_id_coded as enc, order_type, proc_id, description, display_name, authrzing_prov_id,
                    order_inst_jittered as slp_orderInstJTR, proc_start_time_jittered as slp_procStartJTR, last_stand_perf_tm_jittered as slp_procFinalJTR -- order_time_jittered redundant? seems equivalent to order_inst_jittered
    FROM `mining-clinical-decisions.shc_core.order_proc` -- other potential tables to consider: order_proc, procedure_code, proc_orderset
    WHERE (LOWER(order_class) LIKE '%hospital%' OR LOWER(order_class) LIKE '%stanford%' OR LOWER(order_class) LIKE '%point of care%' OR LOWER(order_class) LIKE '%normal%')
    AND ordering_mode = 'Inpatient'

    -- speech therapy
    AND order_type IN ('SLP','REHAB')
    AND proc_id IN (198308,172773,172775,17588,1869,412517,172770,1868,1867,467380,493867,493288)

),

-- collect orders (placed) for SW
socialWork AS
(
    SELECT DISTINCT anon_id, order_proc_id_coded, pat_enc_csn_id_coded as enc, order_type, proc_id, description, display_name, authrzing_prov_id,
                    order_inst_jittered as sw_orderInstJTR, proc_start_time_jittered as sw_procStartJTR, last_stand_perf_tm_jittered as sw_procFinalJTR -- order_time_jittered redundant? seems equivalent to order_inst_jittered
    FROM `mining-clinical-decisions.shc_core.order_proc` -- other potential tables to consider: order_proc, procedure_code, proc_orderset
    WHERE (LOWER(order_class) LIKE '%hospital%' OR LOWER(order_class) LIKE '%stanford%' OR LOWER(order_class) LIKE '%point of care%' OR LOWER(order_class) LIKE '%normal%')
    AND ordering_mode = 'Inpatient'

    -- social work / case management
    AND proc_id IN (25226,35508,48129,189235) -- social work

),

-- answering question: ("Did PT/ST get ordered on 1st day or 4th day? SW consult early or late?")
therapyOrders AS
(
    SELECT  a.enc,
            DATETIME_DIFF(dischTimeJTR, min(rt_orderInstJTR), DAY) as firstRT_daysb4dc,
            DATETIME_DIFF(dischTimeJTR, min(pt_orderInstJTR), DAY) as firstPT_daysb4dc,
            DATETIME_DIFF(dischTimeJTR, min(ot_orderInstJTR), DAY) as firstOT_daysb4dc,
            DATETIME_DIFF(dischTimeJTR, min(slp_orderInstJTR), DAY) as firstSLP_daysb4dc,
            DATETIME_DIFF(dischTimeJTR, min(sw_orderInstJTR), DAY) as firstSW_daysb4dc,
    FROM selectDRGs a
    LEFT JOIN respiratoryTherapy b USING(enc)
    LEFT JOIN physicalTherapy c USING(enc)
    LEFT JOIN occupationalTherapy d USING(enc)
    LEFT JOIN speechTherapy e USING(enc)
    LEFT JOIN socialWork f USING(enc)

    GROUP BY a.anon_id, a.enc, admsnTimeJTR, dischTimeJTR, drg -- mrn, AdmitTRUE, DischTRUE, LOS, Cost_Direct, Cost_Total,


),

-- opioids? total amount of opiates / pain meds consumed? needed opioid withdrawal agents?
opioidOrders AS
(
    SELECT DISTINCT a.anon_id, enc, order_med_id_coded as orderID,
                    order_inst, # order_start_time, order_end_time
                    medication_id as medID, med_description, med_presc_prov_id as prescriber, freq_name,
                    med_route, dose_unit -- use mar::sig for dosage instead of order_med::hv_discrete_dose (range of allowed doses) or order_med::min_discrete_dose (minimum dose allowable)
                    -- total dosage administered
                    -- whether given or not EARLY due to patient request
    FROM selectDRGs a
    LEFT JOIN `mining-clinical-decisions.shc_core.order_med` b
        ON enc = pat_enc_csn_id_coded

    WHERE LOWER(pharm_class_name) LIKE '%opioid%'
    AND LOWER(pharm_class_name) NOT LIKE '%non-opioid%'
    AND thera_class_name IN ('ANALGESICS')
    AND thera_class_name != 'ANTIDOTES' -- remove narcan, naloxone, etc.
    AND med_route_c IN (15,11) -- ('Oral','Intravenous','Transdermal','Feeding Tube','Intramuscular') = (15,11,20,123,6)
    # WHERE LOWER(pharm_class_name) NOT LIKE '%opioid withdrawal%' -- buprenorphine, suboxone

    ORDER BY enc, order_inst
),

-- link to MAR to find total dose administered (over encounter) for order
opioidTotalDose AS
(
    #SELECT infusion_rate, mar_inf_rate_unit, count(*) as n
    SELECT  enc, medID, med_description, med_route, b.dose_unit as dose_unit, sum(CAST(sig as NUMERIC)) as totalDose, max(taken_time_jittered) as lastAdminJTR
    FROM opioidOrders a
    LEFT JOIN `mining-clinical-decisions.shc_core.mar` b
        ON enc = b.mar_enc_csn_coded
        AND a.orderID = b.order_med_id_coded
    WHERE mar_action = 'Given'
    GROUP BY enc, medID, med_description, med_route, b.dose_unit

    ORDER BY enc, med_description, totalDose
),

-- pick the most commonly used opioids; column for last administration of any kind of opioid
opioidsFinal AS
(

    SELECT b.*, a.lastOpioidAdminJTR
    FROM
        (
        SELECT enc, max(lastAdminJTR) as lastOpioidAdminJTR
        FROM opioidTotalDose
        GROUP BY enc
        ) a
    JOIN opioidTotalDose b
    ON a.enc = b.enc

    WHERE medID IN (112586,10814,540106,14632,10813) ##### 80/20 rule --> contains the majority of opioid orders (for drg=001)
),

-- PACU orderset used?
ordersets AS
(
    SELECT DISTINCT enc, SS_SG_NAME as ordersetSmartGroup, protocol_name as ordersetProtocol, min(order_inst) as ordersetTime
                    -- PACU orderset used? Y/N (day of admission)
                    -- ICU PAIN o/s used? Y/N (day of admission)
                    -- PCA o/s used? Y/N (day of admission)
                    -- good idea to pull day of surgery (as day of admission) to help contextualize the above
    FROM SelectDRGs a
    JOIN `mining-clinical-decisions.shc_core.med_orderset` b ON a.enc = b.pat_enc_csn_id_coded
    JOIN `mining-clinical-decisions.shc_core.order_med` c ON a.enc = c.pat_enc_csn_id_coded AND b.order_med_id_coded = c.order_med_id_coded
    WHERE ((LOWER(ss_section_name) LIKE '%pain%' OR LOWER(SS_SG_NAME) LIKE '%pain%' OR LOWER(protocol_name) LIKE '%pain%')
            OR (LOWER(ss_section_name) LIKE '%analg%' OR LOWER(SS_SG_NAME) LIKE '%analg%' OR LOWER(protocol_name) LIKE '%analg%'))
    GROUP BY enc, b.order_med_id_coded, ordersetSmartGroup, ordersetProtocol
    ORDER BY enc, ordersetTime

    /* -- better to use LIKE clauses above which capture many disparate protocols
    AND ss_prl_id IN (4380, -- 'IP ICU PAIN MANAGEMENT'
                      625, --  'ANE PACU'
                      3862, -- 'IP CTS ICU CARDIAC SURGERY POSTOP'
                      946 -- 'IP PAIN PATIENT CONTROLLED ANALGESIA (PCA)'
    )*/

    #GROUP BY ss_section_name, SS_SG_NAME, protocol_name, ss_prl_id ORDER BY n DESC

),

-- acute pain service consulted?
painService AS
(
    SELECT NULL
),

-- OR characteristics?
-- surgical approach, supplies/devices used, etc.
operation AS
(
    SELECT NULL
),

-- Choice of attending?
provider AS
(
    SELECT NULL
),

-- Guideline Adherence for XYZ diagnosis
guidelineXYZ AS
(
    SELECT NULL
),

aggregator AS
(
    SELECT
        mrn, AdmitTRUE, DischTRUE, JITTER, LOS, Cost_Direct, Cost_Total, a.anon_id, a.enc, admsnTimeJTR, dischTimeJTR, drg, drg_c,
        GENDER, CANONICAL_ETHNICITY, CANONICAL_RACE, INTRPTR_NEEDED_YN, INSURANCE_PAYOR_NAME, BMI, CHARLSON_SCORE, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL,
        firstRT_daysb4dc, firstPT_daysb4dc, firstOT_daysb4dc, firstSLP_daysb4dc, firstSW_daysb4dc,
        medID, med_description, med_route, dose_unit, totalDose, lastAdminJTR, lastOpioidAdminJTR,
        ordersetSmartGroup, ordersetProtocol, ordersetTime
    # selectDRG: mrn, AdmitTRUE, DischTRUE, LOS, Cost_Direct, Cost_Total, anon_id, enc, admsnTimeJTR, dischTimeJTR, drg, drg_c
    # patientFactors: ANON_ID, GENDER, CANONICAL_ETHNICITY, CANONICAL_RACE, INTRPTR_NEEDED_YN, INSURANCE_PAYOR_NAME, BMI, CHARLSON_SCORE, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL
    # therapyOrders: enc, firstRT_daysb4dc, firstPT_daysb4dc, firstOT_daysb4dc, firstSLP_daysb4dc, firstSW_daysb4dc,
    # opioidsFinal: enc, medID, med_description, med_route, dose_unit, totalDose, lastAdminJTR, lastOpioidAdminJTR
    # ordersets: enc, ordersetSmartGroup, ordersetProtocol, ordersetTime
    FROM selectDRGs a
    LEFT JOIN patientFactors b ON a.anon_id = b.ANON_ID
    LEFT JOIN therapyOrders c ON a.enc = c.enc
    LEFT JOIN opioidsFinal d ON a.enc = d.enc
    LEFT JOIN ordersets e ON a.enc = e.enc

    ORDER BY a.enc, lastAdminJTR, ordersetTime
)

SELECT * FROM aggregator
