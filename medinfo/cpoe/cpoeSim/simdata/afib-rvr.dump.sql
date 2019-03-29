/* Insert states */
/* Afib-RVR Onset */
insert into sim_state(sim_state_id, name, description)
  values (40, 'Afib-RVR Active', 'Afib-RVR Active');
/* Afib-RVR Stabilized */
insert into sim_state(sim_state_id, name, description)
  values (41, 'Afib-RVR Stabilized', 'Cardioversion improves hemodynamics');
/* Afib-RVR Stabilized No Anti-coag */
insert into sim_state(sim_state_id, name, description)
  values (42, 'Afib-RVR Stabilized No Anti-coag', 'No anticoagulation after cardioversion results in stroke');
/* Afib-RVR Critical Post Diuretics */
insert into sim_state(sim_state_id, name, description)
  values (43, 'Afib-RVR Critical Post Diuretics', 'Diuretics worsen hypotension');
/* Afib-RVR Critical Post Nodal */
insert into sim_state(sim_state_id, name, description)
  values (44, 'Afib-RVR Critical Post Nodal', 'Nodal Agents worsen hypotension');
/* Afib-RVR Metastable */
insert into sim_state(sim_state_id, name, description)
  values (45, 'Afib-RVR Metastable', 'Amio drip (without bolus) slows heart rate');
/* Afib-RVR Stablized Consult */
insert into sim_state(sim_state_id, name, description)
  values (46, 'Afib-RVR Stablized Consult', 'Cardiology consult is ordered');

/* Insert patient record */
insert into sim_patient(sim_patient_id, age_years, gender, name)
  values (49, 66, 'Female', '(Template) Shortness of Breath');
insert into sim_patient_state(sim_patient_state_id, sim_patient_id, sim_state_id, relative_time_start)
  values (121, 49, 40, 0);

/* Insert notes */
/* Initial note */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (3, 2001, 1003, 0, 40, '<h3>CC:</h3>

 Shortness of Breath


 <h3>HPI:</h3>

 <p>66 F hx HTN, HFpEF

 Patient reports shortness of breath since 6am this morning.

 Normally can walk 1/2 mile without shortness of breath.

 Lives alone, called EMS for SOB this morning.

 History of CHF, HTN. States she takes her medications.

 Also reports worsening dizziness since this morning. No chest pain reported.

 EMS noted patient was tachycardic. 5mg IV diltiazem given in the field </p>




 <h3>ROS:</h3>

 Otherwise negative except as per HPI, including;

 Denies fever, chills, chest pain.

 Denies recent travel. Denies orthopnea. Denies leg swelling. Denies dyspnea on exertion.

 Denies weakness/sensory changes.


 <h3>Medical History</h3>

 <ul>

 <li>Hypertension

 <li>CHF

 </ul>



 <h3>Allergies:</h3>

 NKDA



 <h3>Medications:</h3>

 <ul>

 <li>Hydrochlorothiazide

 <li>Ibuprofen PRN

 </ul>



 <h3>Family/Social Hx:</h3>

 Father with a history of coronary artery disease in his 50s

 Denies drug use/alcohol
 ');

/* Afib-RVR Critical Post Diuretics */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 43, 'Patient is lethargic and very short of breath

 <h3>Physical Exam</h3>

 T: 97.9F, BP: 83/59, HR: 153, RR: 24, O2: 92%

 <ul>

 <li>General: <i>Fatigued appearing</i>

 <li>HEENT: <i>No conjunctival pallor.</i> EOMI, PERRL, no mucositis or oral lesions noted.

 <li>Neck: Supple, JVP 9cm above the sternal angle

 <li>Lungs: Significant crackles throughout the lung fields

 <li>Cardiac: <i>Rapid, irregularily irregular</i>  No murmurs, rubs or gallops.

 <li>Abdomen: Soft, non-tender and non-distended without organomegaly.

 <li>Rectal: deferred

 <li>Extremities: <i> cool with 3+ pitting edema</i> No clubbing, cyanosis

 <li>Neuro: <i>Alert and oriented x2, lethargic. </i> Not cooperative with neuro-exam, but moving all extremities.

 <li>Skin: no rashes

 </ul>');

/* Afib-RVR Critical Post Nodal */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 44, 'Patient is lethargic and very short of breath

 <h3>Physical Exam</h3>

 T: 97.9F, BP: 81/59, HR: 123, RR: 30, O2: 89%

 <ul>

 <li>General: <i>Fatigued appearing</i>

 <li>HEENT: <i>No conjunctival pallor.</i> EOMI, PERRL, no mucositis or oral lesions noted.

 <li>Neck: Supple, JVP 9cm above the sternal angle

 <li>Lungs: Significant crackles throughout the lung fields

 <li>Cardiac: <i>Rapid, irregularily irregular</i>  No murmurs, rubs or gallops.

 <li>Abdomen: Soft, non-tender and non-distended without organomegaly.

 <li>Rectal: deferred

 <li>Extremities: <i> cool with 3+ pitting edema</i> No clubbing, cyanosis

 <li>Neuro: <i>Alert and oriented x2, lethargic. </i>. Not cooperative with neuro-exam, but moving all extremities.

 <li>Skin: no rashes

 </ul>');

 /* Afib-RVR Metastable */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 45, 'The patient continues to have mild shortness of breath

 <h3>Physical Exam</h3>

 T: 97.9F, BP: 99/69, HR: 131, RR: 23, O2: 91%

 <ul>

 <li>General: <i>Mildly fatigued appearing</i>

 <li>HEENT: No conjunctival pallor. EOMI, PERRL, no mucositis or oral lesions noted.

 <li>Neck: Supple, JVP 7cm above the sternal angle

 <li>Lungs: Moderate crackles throughout the lung fields, mild wheezing

 <li>Cardiac: <i>Rapid, irregularily irregular</i>  No murmurs, rubs or gallops.

 <li>Abdomen: Soft, non-tender and non-distended without organomegaly.

 <li>Rectal: deferred

 <li>Extremities: <i> cool with 3+ pitting edema</i> No clubbing, cyanosis

 <li>Neuro: Alert and oriented x3, Grossly non-focal. Conversant, moving all extremities. No overt cerebellar signs / incoordination.

 <li>Skin: no rashes

 </ul>');

 /* Afib-RVR Stabilized */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 41, 'Patient breathing and dizziness have improved



 <h3>Physical Exam</h3>

 T: 98.1F, BP: 138/81, HR: 87, RR: 18, O2: 97%

 <ul>

 <li>General: No apparent distress

 <li>HEENT: No conjunctival pallor or scleral icterus.

 <li>Lungs: Slight crackles at the bases bilaterally; no wheezes or rhonchi

 <li>Cardiac: Regular, no murmurs rubs, or gallups

 <li>Abdomen: Soft. Nontender and nondistended.

 <li>Extremities: 1+ DP pulses, warm, 3+ Pitting edema

 <li>Neuro: Alert and oriented. Grossly non-focal. Conversant.

 <li>Skin: No rashes

 </ul>');

/* Afib-RVR Stabilized No Anti-coag */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 42, 'Patient notes R sided weakness and difficulty speaking

 <h3>Physical Exam</h3>

 T: 98.1F, BP: 138/81, HR: 90, RR: 18, O2: 97%

 <ul>

 <li>General: Appears anxious

 <li>HEENT: No conjunctival pallor or scleral icterus.

 <li>Lungs: Slight crackles at the bases bilaterally; no wheezes or rhonchi

 <li>Cardiac: Regular, no murmurs rubs, or gallups

 <li>Abdomen: Soft. Nontender and nondistended.

 <li>Extremities: 1+ DP pulses, warm, 3+ Pitting edema

 <li>Neuro: Alert and oriented x3. Difficulty with word finding and producing words. CN II-XII intact. 3/5 strength in the right upper and right lower extremities. Sensation grossly intact to light touch. Gait not assessed. No dysmetria.

 <li>Skin: No rashes

 </ul>');

/* Afib-RVR Stablized Consult */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (8, 2001, 1500, 0, 46, 'Cardiology recommends anticoagulation following cardioversion and long term maintenance of rhythm control.');

/* Insert state_results */


/* MRI */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (530, 42, 130, 62831, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (531, 42, 130, 46039, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (532, 42, 130, 46065, 'Brain MRI ordered. Scan is pending. Estimated completion in 1 hour.');

insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (533, 42, 131, 62831, 'DWI demonstrates restricted diffusion in the L temporal lobe, R internal capsule, consistent with cardio-embolic stroke.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (534, 42, 131, 46039, 'DWI demonstrates restricted diffusion in the L temporal lobe, R internal capsule, consistent with cardio-embolic stroke.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (535, 42, 131, 46065, 'DWI demonstrates restricted diffusion in the L temporal lobe, R internal capsule, consistent with cardio-embolic stroke.');

/* CT */
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (536, 42, 132, 45804, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (537, 42, 132, 45983, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (538, 42, 132, 48524, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (539, 42, 132, 50241, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (540, 42, 132, 52016, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (541, 42, 132, 64739, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
  insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (542, 42, 132, 65940, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (543, 42, 132, 50098, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (544, 42, 132, 49965, 'Head CT ordered. Scan is pending. Estimated completion in 1 hour.');


insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (545, 42, 133, 45804, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (546, 42, 133, 45983, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (547, 42, 133, 48524, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (548, 42, 133, 50241, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (549, 42, 133, 52016, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (560, 42, 133, 64739, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (561, 42, 133, 65940, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (562, 42, 133, 50098, 'No acute intracranial abnormality.');
insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, text_value)
  values (563, 42, 133, 49965, 'No acute intracranial abnormality.');


/* Insert required result mappings */


/* State transitions */
/* Cardioversion -> Stabilized No-Anticoag */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (50, 40, 42, 65534, 'Cardioversion improves hemodynamics');
/* Anticoagulant -> Stablized */
/* Warfarin */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (51, 42, 41, 44234, 'No anticoagulation after cardioversion results in stroke');
-- /* Apixaban */
-- Not found

/* Rivaroxaban */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (53, 42, 41, 60178, 'No anticoagulation after cardioversion results in stroke');
/* Heparin */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (54, 42, 41, 44359, 'No anticoagulation after cardioversion results in stroke');
/* Enoxaparin */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (55, 42, 41, 44250, 'No anticoagulation after cardioversion results in stroke');
/* Dabigatran */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (56, 42, 41, 54380, 'No anticoagulation after cardioversion results in stroke');
/* Furosemide IV -> Critical Post Diuretics */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (57, 40, 43, 44004, 'Diuretics worsen hypotension');
/* Diltiazem -> Critical Post Nodal*/
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (58, 40, 44, 44393, 'Nodal Agents worsen hypotension');
/* Metoprolol IV push -> Critical Post Nodal */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (59, 40, 44, 44327, 'Nodal Agents worsen hypotension');
/* Amiodarone IV bolus -> Critical Post Nodal */
-- Bolus option not found
/* Amiodarone IV infusion -> Metastable */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (60, 40, 45, 35968, 'Amio drip (without bolus) slows heart rate');
/* Amiodarone pills -> Stabilized */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (61, 40, 41, 44352, 'Maintenance of rhythm with amiodarone');
/* Cardiololgy consult -> Afib-RVR Stablized Consult */
insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
  values (62, 42, 46, 49251, 'Maintenance of rhythm with amiodarone');
