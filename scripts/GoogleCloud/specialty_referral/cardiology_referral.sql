/*
Sub-Aim: 
Estimate patient days and in-person specialty visits consumed while patients await a specialty visits that could be addressed through non-in-person consultations.

Objective: Quantify the relative potential opportunity to expedite patient care and reduce specialty clinic need with virtual (non-in-person) clinical consultation options.
Cohort / Participants: All available pairs of requests for specialty consultation and a respective specialty clinic visit, which excludes cases where the visit includes a billable procedure (e.g., surgical or counseling) are likely not reproducible in the primary referring clinic even with virtual consultation.

Design: Simple descriptive analysis, summing up the outcome quantities, stratified by specialty type and referral diagnosis. For referrals that yield a single,  specialty clinic visit, count the number of days between the referral request and specialty visit towards the total patient days and the one specialty clinic visit. For referrals that yield a specialty clinic visit followed by subsequent visits to the same specialty clinic (e.g., where initial diagnostic workup must be ordered in the first visit, and then followed up for treatment in the subsequent visits), this implies subsequent specialty management was required either way, so the delay until initial specialty care cannot be directly eliminated. This potentially could still have been expedited if the diagnostic workup was initiated in the primary referring clinic. In these cases, count the number of days between the first specialty clinic visit and the subsequent one towards the total patient days and one extra specialty clinic visit consumed.

Potential problems and alternatives: Some clinical orders in specialty clinics would not be reasonable to expect a primary referring clinician to reproduce, even with guidance (e.g., chemotherapy). In addition to excluding cases that yield a billable surgical or counseling procedure, we will exclude cases that generate a clinical order that essentially never arises from within a primary care clinic.

Expected impacts/Products: Estimates of the potential opportunity to benefit from virtual consult systems, and a methodology for estimating wait times for specialty/diagnosis referrals that could further be incorporated into integrated decision support systems.
*/

# Create a Population of Referral: 

# resulting Table: z_sub_aim_referral_table

/*
      SELECT
        a.jc_uid, a.pat_enc_csn_id_coded, a.ordering_date_jittered, a.description,
        b.appt_time_jittered, b.appt_type, b.enc_type, b.visit_type, b.department_id
      FROM
        `datalake_47618.order_proc` as a
      INNER JOIN 
        `datalake_47618.encounter` as b
      ON
        a.pat_enc_csn_id_coded = b.pat_enc_csn_id_coded
      WHERE 
        a.description like 'REFERRAL%' 
*/

# Create a count of each referral 

# resulting table: z1_sub_aim_referral_table

/*
    select count(description) count, description  
    from  `datalake_47618.z_subaim_referral_table` 
    group by description 
    order by count desc
*/

# Create A subcohort study on Cardiology 

# resulting table: z2_subaim_referral_table

/*
    select *
    from  `datalake_47618.z_subaim_referral_table`
    where description like "REFERRAL_TO_CARDIOLOGY"
    and appt_time_jittered > '2014' 
*/ 

# Create a Clinical Department Timeline for Cardiology Referral Patients 

# resulting table: z3_subaim_referral_table

/*
select jc_uid, pat_enc_csn_id_coded, appt_time_jittered as date, department_id, visit_type
from `datalake_47618.encounter`
WHERE jc_uid in 
  (
  select distinct(jc_uid) jc_uid 
  from `datalake_47618.z2_subaim_referral_table`
  )
*/


# Create a Clinical Department Timeline for Cardiology Referral Patients joined on description post 2014

# resulting table: z4_subaim_referral_table

/*
      SELECT
        a.description,
        b.date, b.visit_type, b.jc_uid, b.pat_enc_csn_id_coded, b.department_id
      FROM `datalake_47618.order_proc` as a
      INNER JOIN `datalake_47618.z3_sub_aim_referral_table` as b
      ON a.pat_enc_csn_id_coded = b.pat_enc_csn_id_coded
      where date > '2014'
*/

# New Event Timeline for New Patient from a Cohort of Cardiology 

# resulting table: z5_subaim_referral_table
/*
select * 
from `datalake_47618.z4_subaim_referral_table`
where visit_type like "NEW PATIENT%"
*/
      
# Create Department Map to ID Table 

# resulting table: z6_subaim_referral_table

select department_id, department_name 
from `datalake_47618.dep_map`
