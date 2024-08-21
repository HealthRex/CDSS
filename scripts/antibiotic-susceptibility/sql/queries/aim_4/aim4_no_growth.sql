-- TODO: Get review by Jon/Nick/project people to see if this is good to go/done
CREATE OR REPLACE TABLE `antimicrobial_stewardship.aim4_no_growth` AS

SELECT *
FROM `antimicrobial_stewardship.aim4_base_cohort`
WHERE was_positive = 0;