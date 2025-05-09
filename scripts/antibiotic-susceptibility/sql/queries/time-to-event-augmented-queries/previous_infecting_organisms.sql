##################
## Goal:Creating a table indicates previous infection with a specific pathogen
##################
CREATE OR REPLACE TABLE `antimicrobial_stewardship.microbiology_culture_prior_infecting_organism_augmented` AS (
WITH previous_infecting_organisms AS (
    SELECT
        past_cs.anon_id,
        past_cs.result_time_jittered_utc as prior_infecting_organism_recorded_time,
        CASE WHEN TRIM(past_cs.organism) <> '' THEN TRIM(past_cs.organism) ELSE NULL END AS previous_organisms, -- Trim and handle NULL
    FROM
        `som-nero-phi-jonc101.shc_core_2023.culture_sensitivity` past_cs
    WHERE
         past_cs.organism IN (         
            -- Escherichia
            'ESCHERICHIA COLI', 'ESCHERICHIA COLI (CARBAPENEM RESISTANT)', 'ESCHERICHIA FERGUSONII', 
            'ESCHERICHIA HERMANII', 'ESCHERICHIA SPECIES', 'ESCHERICHIA VULNERIS',
            -- Klebsiella
            'KLEBSIELLA AEROGENES', 'KLEBSIELLA AEROGENES (CARBAPENEM RESISTANT)', 'KLEBSIELLA OXYTOCA', 
            'KLEBSIELLA OZAENAE', 'KLEBSIELLA PNEUMONIAE', 'KLEBSIELLA PNEUMONIAE (CARBAPENEM RESISTANT)',
            'KLEBSIELLA PNEUMONIAE SSP. OZAENAE', 'KLEBSIELLA SPECIES', 'KLEBSIELLA OXYTOCA (CARBAPENEM RESISTANT)',
            -- Enterococcus
            'ENTEROCOCCUS AVIUM', 'ENTEROCOCCUS CASSELIFLAVUS', 'ENTEROCOCCUS DURANS', 
            'ENTEROCOCCUS DURANS/HIRAE', 'ENTEROCOCCUS FAECALIS', 'ENTEROCOCCUS FAECALIS - VANCO RESISTANT',
            'ENTEROCOCCUS FAECIUM', 'ENTEROCOCCUS FAECIUM - VANCO RESISTANT', 'ENTEROCOCCUS FAECIUM -  VANCO RESISTANT',
            'ENTEROCOCCUS GALLINARUM', 'ENTEROCOCCUS RAFFINOSUS', 'ENTEROCOCCUS SPECIES',
            -- Coagulase negative Staphylococcus
            'COAG NEGATIVE STAPHYLOCOCCUS', 'STAPHYLOCOCCUS SPECIES - COAG NEGATIVE, NOT STAPH SAPROPHYTICUS', 
            -- Staphylococcus
            'STAPHYLOCOCCUS AUREUS', 'STAPH AUREUS {MRSA}', 'STAPH AUREUS(COLONY VARIANT - SMALL COLONY OR OTHER MORPHOTYPE)', 
            'STAPHYLOCOCCUS COHNII', 'STAPHYLOCOCCUS EPIDERMIDIS', 'STAPHYLOCOCCUS HAEMOLYTICUS',
            'STAPHYLOCOCCUS LUGDUNENSIS', 'STAPHYLOCOCCUS SAPROPHYTICUS', 'STAPHYLOCOCCUS SPECIES',
            'STAPHYLOCOCCUS SPECIES -NOT STAPH. AUREUS', 'STAPHYLOCOCCUS SPECIES, COAG PENDING',
            -- Proteus
            'PROTEUS MIRABILIS', 'PROTEUS SPECIES', 'PROTEUS VULGARIS GROUP',
            'ZZZPROTEUS PENNERI', 'ZZZPROTEUS VULGARIS',
            -- Enterobacter
            'ENTEROBACTER AMNIGENUS 1', 'ENTEROBACTER ASBURIAE', 'ENTEROBACTER CANCEROGENUS', 
            'ENTEROBACTER CLOACAE', 'ENTEROBACTER CLOACAE COMPLEX', 'ENTEROBACTER CLOACAE COMPLEX (CARBAPENEM RESISTANT)',
            'ENTEROBACTER GERGOVIAE', 'ENTEROBACTER SPECIES', 'ENTEROBACTER TAYLORAE', 'ZZZENTEROBACTER AEROGENES',
            -- Citrobacter
            'CITROBACTER AMALONATICUS COMPLEX', 'CITROBACTER BRAAKII', 'CITROBACTER FREUNDII',
            'CITROBACTER FREUNDII COMPLEX', 'CITROBACTER FREUNDII COMPLEX (CARBAPENEM RESISTANT)',
            'CITROBACTER KOSERI', 'CITROBACTER KOSERI (CARBAPENEM RESISTANT)', 'CITROBACTER SPECIES',
            'CITROBACTER YOUNGAE', 'ZZZCITROBACTER KOSERI',
            -- Streptococcus
            'STREPTOCOCCUS AGALACTIAE', 'STREPTOCOCCUS AGALACTIAE (GROUP B)', 'STREPTOCOCCUS AGALACTIAE {GROUP B}',
            'STREPTOCOCCUS ANGINOSUS GROUP', 'STREPTOCOCCUS BOVIS/EQUINUS COMPLEX', 'STREPTOCOCCUS CANIS',
            'STREPTOCOCCUS CONSTELLATUS', 'STREPTOCOCCUS DYSGALACTIAE', 'STREPTOCOCCUS DYSGALACTIAE/EQUISIMILIS',
            'STREPTOCOCCUS EQUI', 'STREPTOCOCCUS GORDONII', 'STREPTOCOCCUS GRAM (+) GROUP', 'STREPTOCOCCUS GROUP A',
            'STREPTOCOCCUS GROUP B', 'STREPTOCOCCUS GROUP C', 'STREPTOCOCCUS GROUP D', 'STREPTOCOCCUS GROUP F',
            'STREPTOCOCCUS GROUP G', 'STREPTOCOCCUS INFANTARIUS', 'STREPTOCOCCUS INFANTIS', 'STREPTOCOCCUS INTERMEDIUS',
            'STREPTOCOCCUS MITIS', 'STREPTOCOCCUS MITIS GROUP', 'STREPTOCOCCUS MITIS/STREPTOCOCCUS ORALIS',
            'STREPTOCOCCUS MUTANS', 'STREPTOCOCCUS MUTANS GROUP', 'STREPTOCOCCUS ORALIS', 'STREPTOCOCCUS PARASANGUINIS',
            'STREPTOCOCCUS PNEUMONIAE', 'STREPTOCOCCUS PYOGENES (GROUP A)', 'STREPTOCOCCUS PYOGENES {GROUP A}',
            'STREPTOCOCCUS SALIVARIUS', 'STREPTOCOCCUS SALIVARIUS GROUP', 'STREPTOCOCCUS SANGUINIS',
            'STREPTOCOCCUS SANGUIS', 'STREPTOCOCCUS SPECIES', 'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC',
            'STREPTOCOCCUS SPECIES - ALPHA HEMOLYTIC, NOT S.PNEUMO', 'ZZZSTREPTOCOCCUS GALLOLYTICUS SUBSP. GALLOLYTICUS',
            'ZZZSTREPTOCOCCUS GALLOLYTICUS SUBSP. PASTEURIANUS', 'VIRIDANS GROUP STREPTOCOCCI',
            'STREPTOCOCCUS ANGINOSUS', 'STREPTOCOCCUS BOVIS GP.', 'STREPTOCOCCUS GALLOLYTICUS',
            -- Pseudomonas
            'MUCOID PSEUDOMONAS AERUGINOSA', 'PSEUDOMONAS AERUGINOSA', 'PSEUDOMONAS AERUGINOSA (NON-MUCOID CF)',
            'PSEUDOMONAS FLUORESCENS', 'PSEUDOMONAS FLUORESCENS GROUP', 'PSEUDOMONAS MENDOCINA',
            'PSEUDOMONAS ORYZIHABITANS', 'PSEUDOMONAS PUTIDA', 'PSEUDOMONAS PUTIDA GROUP',
            'PSEUDOMONAS SPECIES', 'PSEUDOMONAS SPECIES - FLUORESCENS/PUTIDA GROUP',
            'PSEUDOMONAS SPECIES - NOT P.AERUGINOSA', 'PSEUDOMONAS STUTZERI', 'PSEUDOMONAS STUTZERI GROUP',
            -- Acinetobacter
            'ACINETOBACTER BAUMANNII', 'ACINETOBACTER BAUMANNII COMPLEX', 'ACINETOBACTER HAEMOLYTICUS',
            'ACINETOBACTER LWOFFI', 'ACINETOBACTER SPECIES',
            -- Providencia
            'PROVIDENCIA RETTGERI', 'PROVIDENCIA SPECIES', 'PROVIDENCIA STUARTII',
            -- Serratia
            'SERRATIA LIQUEFACIENS', 'SERRATIA MARCESCENS', 'SERRATIA MARCESCENS (CARBAPENEM RESISTANT)',
            'SERRATIA ODORIFERA', 'SERRATIA PLYMUTHICA', 'SERRATIA RUBIDAEA', 'SERRATIA SPECIES',
            -- Morganella
            'MORGANELLA MORGANII',
            -- Stenotrophomonas
            'STENOTROPHOMONAS MALTOPHILIA',
            -- Candida
            'CANDIDA ALBICANS', 'CANDIDA DUBLINIENSIS', 'CANDIDA FAMATA', 'CANDIDA GLABRATA',
            'CANDIDA GUILLIERMONDII', 'CANDIDA KEFYR', 'CANDIDA KRUSEI', 'ZZZCANDIDA PARAPSILOSIS',
            'CANDIDA LIPOL', 'CANDIDA PARAPSILOSIS COMPLEX', 'CANDIDA TROPICALIS')
),
previous_infecting_organisms_category as (
SELECT anon_id, 
prior_infecting_organism_recorded_time,
CASE 
    WHEN upper(previous_organisms) LIKE '%ESCHERICHIA%' THEN 'Escherichia'
    WHEN upper(previous_organisms) LIKE '%KLEBSIELLA%' THEN 'Klebsiella'
    WHEN upper(previous_organisms) LIKE '%ENTEROCOCCUS%' THEN 'Enterococcus'
    WHEN upper(previous_organisms) LIKE '%COAG NEGATIVE%' THEN 'CONS'
    WHEN upper(previous_organisms) LIKE '%STAPH%' AND previous_organisms NOT LIKE '%COAG NEGATIVE%' THEN 'Staphylococcus'
    WHEN upper(previous_organisms) LIKE '%PROTEUS%' THEN 'Proteus'
    WHEN upper(previous_organisms) LIKE '%ENTEROBACTER%' THEN 'Enterobacter'
    WHEN upper(previous_organisms) LIKE '%CITROBACTER%' THEN 'Citrobacter'
    WHEN upper(previous_organisms) LIKE '%STREPTOCOCC%' THEN 'Streptococcus'
    WHEN upper(previous_organisms) LIKE '%PSEUDOMONAS%' THEN 'Pseudomonas'
    WHEN upper(previous_organisms) LIKE '%ACINETOBACTER%' THEN 'Acinetobacter'
    WHEN upper(previous_organisms) LIKE '%PROVIDENCIA%' THEN 'Providencia'
    WHEN upper(previous_organisms) LIKE '%SERRATIA%' THEN 'Serratia'
    WHEN upper(previous_organisms) LIKE '%MORGANELLA%' THEN 'Morganella'
    WHEN upper(previous_organisms) LIKE '%STENOTROPHOMONAS%' THEN 'Stenotrophomonas'
    WHEN upper(previous_organisms) LIKE '%CANDIDA%' THEN 'Candida'
END AS prior_organism
FROM previous_infecting_organisms
)
select c.anon_id,
c.pat_enc_csn_id_coded,
c.order_proc_id_coded,
c.order_time_jittered_utc,
TIMESTAMP_DIFF(c.order_time_jittered_utc, past_cs.prior_infecting_organism_recorded_time, DAY) as prior_infecting_organism_days_to_culutre,
past_cs.prior_infecting_organism_recorded_time,
past_cs.prior_organism,
from `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_cohort` c
left join previous_infecting_organisms_category past_cs using(anon_id)
where 
TIMESTAMP_DIFF(c.order_time_jittered_utc, past_cs.prior_infecting_organism_recorded_time, DAY)>0
group by c.anon_id,c.pat_enc_csn_id_coded,c.order_proc_id_coded,c.order_time_jittered_utc,past_cs.prior_organism,past_cs.prior_infecting_organism_recorded_time
order by c.anon_id,c.pat_enc_csn_id_coded,c.order_proc_id_coded,c.order_time_jittered_utc,past_cs.prior_organism,past_cs.prior_infecting_organism_recorded_time
)
