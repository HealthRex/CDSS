SELECT DISTINCT description, 
CASE WHEN description LIKE "BLOOD CULT%" THEN 1 
WHEN description IN ("URINE CULTURE", "URINE CULTURE (MENLO)", "URINE CULTURE AND GRAM STAIN", "URINE SENSITIVITIES (MENLO)") THEN 1
WHEN description IN ("FLUID CULTURE / BB GRAM STAIN", "FLUID CULTURE AND GRAM STAIN") THEN 1
WHEN description IN ("CSF CULTURE AND GRAM STAIN", "CULTURE AND GRAM STAIN, CSF") THEN 1
ELSE 0 END include,
# This column may be userful later to see how analysis changes when we decide not to ignore results from all other cultures.
CASE WHEN description LIKE "BLOOD CULT%" THEN 1 
WHEN description IN ("URINE CULTURE", "URINE CULTURE (MENLO)", "URINE CULTURE AND GRAM STAIN", "URINE SENSITIVITIES (MENLO)") THEN 1
WHEN description IN ("FLUID CULTURE / BB GRAM STAIN", "FLUID CULTURE AND GRAM STAIN") THEN 1
WHEN description IN ("CSF CULTURE AND GRAM STAIN", "CULTURE AND GRAM STAIN, CSF") THEN 1
ELSE 0 END affects_not_infected_label
FROM `shc_core.order_proc` 
WHERE order_type LIKE "Microbiology%"
ORDER BY description