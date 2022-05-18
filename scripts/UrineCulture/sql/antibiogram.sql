WITH organism_suscept_long AS (
    SELECT DISTINCT
        order_proc_id_coded, organism, 
        -- Reformat name so SQL doesn't get uspet in pivot operation
        CASE WHEN antibiotic = 'Trimethoprim/Sulfamethoxazole.' 
        THEN 'Trimethoprim_Sulfamethoxazole' 
        ELSE antibiotic END antibiotic,
        CASE WHEN suscept = 'Susceptible' 
        THEN 1 ELSE 0 END suscept
    FROM  
        `mining-clinical-decisions.shc_core.culture_sensitivity`
    WHERE
        description = "URINE CULTURE"
    AND
        organism in ('ESCHERICHIA COLI', 'KLEBSIELLA PNEUMONIAE',
                     'PROTEUS MIRABILIS', 'PSEUDOMONAS AERUGINOSA')
    AND 
        antibiotic in ('Gentamicin', 'Ciprofloxacin', 'Ampicillin',
                       'Nitrofurantoin', 'Trimethoprim/Sulfamethoxazole.')
),

num_tests AS (
    SELECT 
        *
    FROM 
    (
    SELECT 
        organism, antibiotic, suscept
    FROM 
        organism_suscept_long
    )
    PIVOT (
        COUNT(suscept) as num_tests
        FOR antibiotic in ('Gentamicin', 'Ciprofloxacin', 'Ampicillin', 
                           'Nitrofurantoin', 'Trimethoprim_Sulfamethoxazole')
    )
),

frac_suscept AS (
    SELECT 
        *
    FROM 
    (
    SELECT 
        organism, antibiotic, suscept
    FROM 
        organism_suscept_long
    )
    PIVOT (
        AVG(suscept) as frac_suscept
        FOR antibiotic in ('Gentamicin', 'Ciprofloxacin', 'Ampicillin',
                           'Nitrofurantoin', 'Trimethoprim_Sulfamethoxazole')
    )
)

SELECT 
    organism, num_tests_Gentamicin, frac_suscept_Gentamicin,
    num_tests_Ciprofloxacin, frac_suscept_Gentamicin, num_tests_Ampicillin,
    frac_suscept_Ampicillin, num_tests_Nitrofurantoin,
    frac_suscept_Nitrofurantoin, num_tests_Trimethoprim_Sulfamethoxazole,
    frac_suscept_Trimethoprim_Sulfamethoxazole
FROM 
    num_tests
INNER JOIN
    frac_suscept
USING
    (organism)