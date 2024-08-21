-- TODO: Modify the below query to actually identify overtreatment cases
CREATE OR REPLACE TABLE `antimicrobial_stewardship.aim4_no_growth` AS

SELECT *
FROM `antimicrobial_stewardship.aim4_base_cohort`
WHERE was_positive = 1
-- Additional inclusion/exclusion criteria and logic goes here! Good luck, future Nikhil!
WHERE susceptibility LIKE 'Susceptbile' 
    /* OR susceptibility LIKE 'Intermediate' */
;