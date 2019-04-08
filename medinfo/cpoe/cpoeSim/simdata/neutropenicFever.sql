/* Insert states */
/* Neutropenic Fever active state */
insert into sim_state(sim_state_id, name, description)
  values (5000, 'Neutropenic Fever', 'Neutropenic Fever Active');
/* Neutropenic Fever adequately treated state */
insert into sim_state(sim_state_id, name, description)
  values (5001, 'Neutropenic Fever Treated with ABX', 'Appropriate antibiotic improve patient condition');
/* Neutropenic Fever inadequately treated state */
insert into sim_state(sim_state_id, name, description)
  values (5002, 'Neutropenic Fever Treated with IVX', 'Appropriate IVX improve patient condition');
/* Neutropenic Fever inadequately treated state */
insert into sim_state(sim_state_id, name, description)
  values (5003, 'Neutropenic Fever Treated with IVX + ABX', 'Appropriate Treatments for patient condition');


/* Insert patient record */
insert into sim_patient(sim_patient_id, age_years, gender, name)
  values (50, 30, 'Male', '(Template) Fever Symptoms');
insert into sim_patient_state(sim_patient_state_id, sim_patient_id, sim_state_id, relative_time_start)
  values (121, 50, 5000, 0);

/* Insert notes */
/* Initial note */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (3, 2001, 1003, 0, 5000, '<h3>CC:</h3>
Fevers
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
  values (2, 2001, 1500, 0, 5001, 'FEVER IMPROVING Patient feels headache may be worsening, is having a hard time keeping her eyes open with the lights on in the room.
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
   values (2, 2001, 1500, 0, 5002, 'FEVER IMPROVING A LITTLE The patient still feels very tired but has defervesced and overall feels less uncomfortable.
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
    values (2, 2001, 1500, 120, 5003, 'FEVER ALL MO BETTER The patient continues to feel worse, and her nurse orders an RRT.  The MICU fellow responds and recommends changing the empiric regimen for bacterial meningitis to vancomycin and ceftriaxone, to be given stat.
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

 /* State transitions */
 /* IVX -> IVX */
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values (60, 5000, 5001, 35733, 'Appropriate antibiotics improve patient condition'); -- CHANGE TO CORRRECT THING
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values (61, 5000, 5002, 36210, 'Appropriate antibiotics improve patient condition');
 /* IV Cefepime -> adequately treated */
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values (62, 5001, 5003, 36210, 'Appropriate antibiotics improve patient condition');
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values (63, 5002, 5003, 35733, 'Appropriate antibiotics improve patient condition');
 /* IV ABX Meropenem -> adequately treated */
