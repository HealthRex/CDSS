/* Insert states */
/* Meningitis active state */
insert into sim_state(sim_state_id, name, description)
  values (30, 'Mening Active', 'Meningitis Active');
/* Meningitis adequately treated state */
insert into sim_state(sim_state_id, name, description)
  values (31, 'Meningitis Adequately Treated', 'Appropriate antibiotic improve patient condition');
/* Meningitis inadequately treated state */
insert into sim_state(sim_state_id, name, description)
  values (32, 'Meningits Inadequately Treated', 'Inadequate treatment worsens patient condition');
/* Meningitis worsens after an hour */
insert into sim_state(sim_state_id, name, description)
  values (33, 'Meningits Worsens', 'Patient condition worsens after 1 hr');

/* Insert patient record */
insert into sim_patient(sim_patient_id, age_years, gender, name)
  values (48, 25, 'Female', '(Template) Neck Stiffness');
insert into sim_patient_state(sim_patient_state_id, sim_patient_id, sim_state_id, relative_time_start)
  values (120, 48, 30, 0);

/* Insert notes */
/* Initial note */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (3, 2001, 1003, 0, 30, '<h3>CC:</h3>

Fevers, headache and neck stiffness


 <h3>HPI:</h3>

 <p>25 year-old woman, no significant PMH, who was at her job as an office assistant when she experienced the acute onset of high fevers, headaches, photophobia and neck stiffness.  She has not traveled recently or been around any one sick recently.  She believes she is up to date on all recommended vaccinations.



 <h3>ROS:</h3>

 Otherwise negative except as per HPI, including:

 Reports no new rashes.





 <h3>Medical History</h3>

 <ul>

 Healthy, sees her primary care physician regularly.

 </ul>



 <h3>Allergies:</h3>

 NKDA



 <h3>Medications:</h3>

 <ul>

 <li>OCP

 </ul>



 <h3>Family/Social Hx:</h3>

Parents both alive, both with history of HTN and DM.  One brother, healthy.  No tobacco or EtOH.  No history of high risk sexual behaviors, currently not sexually active.');

/* Meningitis active (worse) */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 33, 'Patient feels headache may be worsening, is having a hard time keeping her eyes open with the lights on in the room.




 <h3>Physical Exam</h3>

 T: 102.1F, BP: 98/62, HR: 115, RR: 19, O2: 96%

 <ul>

 <li>General: <i>Appears uncomfortable, eyes closed, lying in bed.</i>

 <li>HEENT: <i>Ability to perform flexion/extension of neck limited.</i> EOMI, PERRL, no mucositis or oral lesions noted.

 <li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.

 <li>Cardiac: <i>Rapid</i> but Regular rate and rhythm. No murmurs, rubs or gallops.

 <li>Abdomen: Soft, non-tender, non-distended. <i>

 <li>Extremities: No clubbing, cyanosis, edema. 1+ DP pulses.

 <li>Neuro: Alert and oriented, although uncomfortable and a bit somnolent. CN II-XII intact. Conversant, moving all extremities. No overt cerebellar signs / incoordination. <i>

 <li>Skin: <i>No rashes.</i>

 </ul>');

/* Meningitis adequately treated */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
   values (2, 2001, 1500, 0, 31, 'The patient still feels very tired but has defervesced and overall feels less uncomfortable.
 <h3>Physical Exam</h3>

 T: 100.1F, BP: 110/70, HR: 95, RR: 16, O2: 96%

 <ul>

 <li>General: <i>Appears mildly uncomfortable but improved from prior, eyes open most of the time, lying in bed.</i>

 <li>HEENT: <i>Ability to perform flexion/extension of neck limited.</i> EOMI, PERRL, no mucositis or oral lesions noted.

 <li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.

 <li>Cardiac: <i>Rapid</i> but Regular rate and rhythm. No murmurs, rubs or gallops.

 <li>Abdomen: Soft, non-tender, non-distended. <i>

 <li>Extremities: No clubbing, cyanosis, edema. 1+ DP pulses.

 <li>Neuro: Alert and oriented, although mildly uncomfortable. CN II-XII intact. Conversant, moving all extremities. No overt cerebellar signs / incoordination. <i>

 <li>Skin: <i>No rashes.</i>

 </ul>');

 /* Meningitis inadequately treated */
 insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
    values (2, 2001, 1500, 1800, 32, 'The patient continues to feel worse, and her nurse orders an RRT.  The MICU fellow responds and recommends changing the empiric regimen for bacterial meningitis to vancomycin and ceftriaxone, to be given stat.
 T: 103.1F, BP: 86/52, HR: 128, RR: 21, O2: 96%

 <ul>

 <li>General: <i>Appears uncomfortable, eyes closed, lying in bed.</i>

 <li>HEENT: <i>Ability to perform flexion/extension of neck limited.</i> EOMI, PERRL, no mucositis or oral lesions noted.

 <li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.

 <li>Cardiac: <i>Rapid</i> but Regular rate and rhythm. No murmurs, rubs or gallops.

 <li>Abdomen: Soft, non-tender, non-distended. <i>

 <li>Extremities: No clubbing, cyanosis, edema. 1+ DP pulses.

 <li>Neuro: Alert and oriented, although quite uncomfortable and a bit somnolent. CN II-XII intact. Conversant, moving all extremities. No overt cerebellar signs / incoordination. <i>

 <li>Skin: <i>No rashes.</i>

 </ul>');


/* Insert state_results */
/* ALB */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (400, 30, 13270, 48744, 4, 'Normal');

/* ALKP */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (401, 30, 13260, 49026, 100, 'Normal');

/* ALT */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (402, 30, 13250, 48831, 30, 'Normal');

/* AST */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (403, 30, 13240, 50163, 30, 'Normal');

/* BUN */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (404, 30, 13050, 48917, 30, 'High');

/* CR */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (405, 30, 13060, 48574, 1.5, 'High');

/* DBIL */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (406, 30, 13220, 46048, 1, 'Normal');

/* ETOH */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (407, 30, 13830, 46048, 0, 'Normal');


/* TBIL */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (408, 30, 13210, 48645, 1, 'Normal');

/* TNI */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value, result_flag)
  values (409, 30, 13530, 45870, '<0.01', 'Normal');

/* INR */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (410, 30, 12040, 45942, 1.1, 'Normal');

/* PT */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (411, 30, 12030, 45759, 15, 'Normal');


/* HCT */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (412, 30, 11020, 45891, 40, 'Normal');

/* HGB */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (413, 30, 11010, 46051, 13, 'Normal');

/* PLT */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (414, 30, 11030, 46090, 88, 'Low');

/* WBC */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (415, 30, 11000, 65835, 18, 'High');

/* LACTATE */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (416, 30, 13504, 62151, 2.3, 'High');

/* WBCCSF */
/* For lp before antiobiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (417, 30, 1000129, 48880, 'WBCCSF 1500, Neutrophil 98%');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (418, 32, 1000129, 48880, 'WBCCSF 1500, Neutrophil 98%');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (419, 33, 1000129, 48880, 'WBCCSF 1500, Neutrophil 98%');
/* For lp after antiobiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (420, 31, 1000129, 48880, 'WBCCSF 1500, Neutrophil 98%');

/* LACCSF */
/* For lp before antiobiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (421, 30, 1000330, 50510, 15);
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (422, 32, 1000330, 50510, 15);
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (423, 33, 1000330, 50510, 15);
/* For lp after antiobiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (424, 31, 1000330, 50510, 15, 'High');


/* No opening pressure clinical item found
insert into sim_result(sim_result_id, name) before antiobiotics
  values (123, 'Opening Pressure');
insert into sim_result(sim_result_id, name) after antibiotics
  values (124, 'Opening Pressure');
*/


insert into sim_result(sim_result_id, name, description, group_string) /* before antibiotics */
  values (125, 'Gram Stain and Culture', 'CULTURE AND GRAM STAIN, CSF', 'BODY FLUID ORDERABLES>Other>CULTURE AND GRAM STAIN, CSF');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (425, 30, 125, 49083, 'Rare Gram Positive Diplococci, many neutrophils');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (426, 32, 125, 49083, 'Rare Gram Positive Diplococci, many neutrophils');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (427, 33, 125, 49083, 'Rare Gram Positive Diplococci, many neutrophils');
/* after antibiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (428, 31, 125, 49083, 'Moderate neutrophils, no organisms seen');

/* TPCSF */
/* before antibiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (429, 30, 1000156, 49020, 200);
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (430, 32, 1000156, 49020, 200);
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (431, 33, 1000156, 49020, 200);
/* after antibiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (432, 31, 1000156, 49020, 200, 'High');

/* GLUCSF */
/* before antibiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (433, 30, 1000155, 48577, 10);
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (434, 32, 1000155, 48577, 10);
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value)
  values (435, 33, 1000155, 48577, 10);
/* after antibiotics */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, result_flag)
  values (436, 31, 1000155, 48577, 10, 'Low');


/* MRI */
insert into sim_result(sim_result_id, name, description, group_string)
  values (130, 'MRI Brain Pending', 'MRI Brain Pending Notification', 'IMAGING>MRI');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (437, 30, 130, 62831, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (438, 30, 130, 46039, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (439, 30, 130, 46065, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (440, 32, 130, 62831, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (441, 32, 130, 46039, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (442, 32, 130, 46065, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');

insert into sim_result(sim_result_id, name, description, group_string)
  values (131, 'MRI Brain', 'MRI Brain', 'IMAGING>MRI');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (443, 30, 131, 62831, 'Questionable subtle diffuse meningeal enhancement.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (444, 30, 131, 46039, 'Questionable subtle diffuse meningeal enhancement.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (445, 30, 131, 46065, 'Questionable subtle diffuse meningeal enhancement.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (446, 32, 131, 62831, 'Questionable subtle diffuse meningeal enhancement.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (447, 32, 131, 46039, 'Questionable subtle diffuse meningeal enhancement.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (448, 32, 131, 46065, 'Questionable subtle diffuse meningeal enhancement.');

/* CT */
insert into sim_result(sim_result_id, name, description, group_string)
  values (132, 'CT Head Pending', 'CT Head Pending Notification', 'IMAGING>CT');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (449, 30, 132, 45804, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (450, 30, 132, 45983, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (451, 30, 132, 48524, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (452, 30, 132, 50241, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (453, 30, 132, 52016, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (454, 30, 132, 64739, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (455, 30, 132, 65940, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (456, 30, 132, 50098, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (457, 30, 132, 49965, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (458, 32, 132, 45804, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (459, 32, 132, 45983, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (460, 32, 132, 48524, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (461, 32, 132, 50241, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (462, 32, 132, 52016, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (463, 32, 132, 64739, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (464, 32, 132, 65940, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (465, 32, 132, 50098, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (466, 32, 132, 49965, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');

insert into sim_result(sim_result_id, name, description, group_string)
  values (133, 'CT Head', 'CT Head', 'IMAGING>CT');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (467, 30, 133, 45804, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (468, 30, 133, 45983, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (469, 30, 133, 48524, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (470, 30, 133, 50241, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (471, 30, 133, 52016, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (472, 30, 133, 64739, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
    insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (473, 30, 133, 65940, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (474, 30, 133, 50098, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (475, 30, 133, 49965, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (476, 32, 133, 45804, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (477, 32, 133, 45983, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (478, 32, 133, 48524, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (479, 32, 133, 50241, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (480, 32, 133, 52016, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (481, 32, 133, 64739, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
    insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (482, 32, 133, 65940, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (483, 32, 133, 50098, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
    values (484, 32, 133, 49965, 'Preliminary read: No hemorrhage or evidence of ischemic stroke.');

/* Do same for neck CT? */


/* Insert required result mappings */
/* CSF CULTURE AND GRAM STAIN */
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8068, 49083, 125, 900);

/* MRI */
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8071, 62831, 130, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8072, 46039, 130, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8073, 46065, 130, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8074, 62831, 130, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8075, 46039, 130, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8076, 46065, 130, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8077, 62831, 131, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8078, 46039, 131, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8079, 46065, 131, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8080, 62831, 131, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8081, 46039, 131, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8082, 46065, 131, 3600);

/* CT */
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8083, 45804, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8084, 45983, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8085, 48524, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8086, 50241, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8087, 52016, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8088, 64739, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8089, 65940, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8090, 50098, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8091, 49965, 132, 0);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8092, 45804, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8093, 45983, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8094, 48524, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8095, 50241, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8096, 52016, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8097, 64739, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8098, 65940, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8099, 50098, 133, 3600);
insert into sim_order_result_map(sim_order_result_map_id, clinical_item_id, sim_result_id, turnaround_time)
  values (8100, 49965, 133, 3600);

/* State transitions */
/* IV Ceftriaxone -> adequately treated */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (40, 30, 31, 35733, 'Appropriate antibiotics improve patient condition');
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (41, 32, 31, 35733, 'Appropriate antibiotics improve patient condition');
/* IV Cefepime -> adequately treated */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (42, 30, 31, 36210, 'Appropriate antibiotics improve patient condition');
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (43, 32, 31, 36210, 'Appropriate antibiotics improve patient condition');
/* IV Meropenem -> adequately treated */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (44, 30, 31, 44008, 'Appropriate antibiotics improve patient condition');
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (45, 32, 31, 44008, 'Appropriate antibiotics improve patient condition');


/* 1hr later -> State worsens */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, time_trigger, description)
  values (46, 30, 33, 3600, 'Patient condition worsens after 1 hr of inadquate empiric treatment');
/* 2hr later -> Inadequately treated */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, time_trigger, description)
  values (47, 30, 32, 7200, 'Inadequate empiric treatment worsens patient condition');
