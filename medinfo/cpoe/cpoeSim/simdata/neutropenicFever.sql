/* Insert states */
/* Neutropenic Fever states (not that had a prior Neutropenic Fever example this is based on, but this adds state transitions) */
insert into sim_state(sim_state_id, name, description)
  values (5000, 'Neutropenic Fever v2', 'Neutropenic Fever (v2 example) Initial State');
insert into sim_state(sim_state_id, name, description)
  values (5001, 'Neutropenic Fever Treated with Abx', 'Appropriate antibiotic improve patient condition');
insert into sim_state(sim_state_id, name, description)
  values (5002, 'Neutropenic Fever Treated with IVF', 'Appropriate IVF improve patient condition');
insert into sim_state(sim_state_id, name, description)
  values (5003, 'Neutropenic Fever Treated with IVF + ABX', 'Appropriate Treatments for patient condition');


/* Insert patient record */
insert into sim_patient(sim_patient_id, age_years, gender, name)
  values (50, 30, 'Male', '(Template) Chemo Fever v2');
insert into sim_patient_state(sim_patient_state_id, sim_patient_id, sim_state_id, relative_time_start)
  values (121, 50, 5000, 0);

/* Insert notes */
/* Initial note */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (3, 2001, 1003, 0, 5000, '<h3>CC:</h3>
Fever and chills

<h3>HPI:</h3>
<p>32M recent dx DLBCLymphoma and underwent first cycle of R-CHOP chemotherapy 10 days ago.
<p>Patient seen at infusion center today for labs and PICC line dressing change.
<p>Patient reporting new-onset high fever, chills, and rigors, for past few hours but no other focal symptoms.
Labs in clinic today noted WBC 0.8, Hgb 11, Plt 96 with an absolute neutrophil count of 80.
Patient direct admitted to the hospital for febrile neutropenia.


<h3>Medical History</h3>
<ul>
<li>Diffuse Large B-Cell Lymphoma
</ul>

<h3>Allergies:</h3>
NKDA

<h3>Medications:</h3>
<ul>
<li>Rituximab, Cyclophosphamide, Doxorubicin, Vincristine, Prednisone
</ul>

<h3>Family/Social Hx:</h3>
No known family history of heme malignancy.
Mother and father alive in 60s with serious medical isues. Two siblings, aged 37 and 28.

<h3>Physical Exam</h3>
T: 102F, BP: 90/57, HR: 126, RR: 24, O2: 98%
<ul>
<li>General: Shivering, wrapped in blankets in bed
<li>HEENT: EOMI, PERRL, no mucositis or oral lesions noted
<li>Neck: Supple, <i>shotty lymphdenopathy</i>, JVP ~6cm
<li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.
<li>Cardiac: <i>Rapid</i> but Regular rate and rhythm. No murmurs, rubs or gallops. 
<li>Abdomen: Soft, non-tender, non-distended. Normo-active bowel sounds. No organomegaly or masses noted
<li>Rectal: No perirectal abscess or lesions
<li>Extremities: No clubbing, cyanosis, edema. <i>Cool feet. Thready DP pulses.</i>
<li>Neuro: Alert and oriented. Grossly non-focal. Conversant, moving all extremities. No overt cerebellar signs / incoordination.
<li>Skin: No rashes or lesions noted.
<li>Lines: <i>R arm PICC line</i> without surrounding erythema, drainage, or tenderness
</ul>');

/* Neutropenic Fever got Abx but not IVF */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
  values (2, 2001, 1500, 0, 5001, 'Patient reports feeling less hot, but still lightheaded.
 <h3>Physical Exam</h3>
 T: 99F, BP: 92/61, HR: 119, RR: 19, O2: 96%
 <ul>
<li>General: Tired, ill appearing
<li>HEENT: EOMI, PERRL, no mucositis or oral lesions noted
<li>Neck: Supple, shotty lymphdenopathy, JVP ~6cm
<li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.
<li>Cardiac: <i>Rapid</i> but Regular rate and rhythm. No murmurs, rubs or gallops. 
<li>Abdomen: Soft, non-tender, non-distended. Normo-active bowel sounds. No organomegaly or masses noted
<li>Rectal: No perirectal abscess or lesions
<li>Extremities: No clubbing, cyanosis, edema. <i>Cool feet. Thready DP pulses.</i>
<li>Neuro: Alert and oriented. Grossly non-focal. Conversant, moving all extremities. No overt cerebellar signs / incoordination.
<li>Skin: No rashes or lesions noted.
<li>Lines: R arm PICC line without surrounding erythema, drainage, or tenderness
 </ul>');

/* Neutropenic Fever got IVF but no Abx */
insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
   values (2, 2001, 1500, 0, 5002, 'Patient feels more awake, but still hot and lousy.
 <h3>Physical Exam</h3>
 T: 101.8F, BP: 105/70, HR: 98, RR: 16, O2: 96%
 <ul>
<li>General: Sweating
<li>HEENT: EOMI, PERRL, no mucositis or oral lesions noted
<li>Neck: Supple, shotty lymphdenopathy, JVP ~8cm
<li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.
<li>Cardiac: Regular rate and rhythm. No murmurs, rubs or gallops. 
<li>Abdomen: Soft, non-tender, non-distended. Normo-active bowel sounds. No organomegaly or masses noted
<li>Rectal: No perirectal abscess or lesions
<li>Extremities: No clubbing, cyanosis, edema. 1+ DP pulses.
<li>Neuro: Alert and oriented. Grossly non-focal. Conversant, moving all extremities. No overt cerebellar signs / incoordination.
<li>Skin: No rashes or lesions noted.
<li>Lines: R arm PICC line without surrounding erythema, drainage, or tenderness
 </ul>');

 /* Neutropenic Fever got Abx and IVF */
 insert into sim_note(note_type_id, author_type_id, service_type_id, relative_state_time, sim_state_id, content)
    values (2, 2001, 1500, 120, 5003, 'Patient reports feeling relatively better, not so hot or lightheaded, and would just like to rest now.
 T: 98.8F, BP: 116/75, HR: 84, RR: 14, O2: 97%
 <ul>
<li>General: Improved, resting comfortably on bed
<li>HEENT: EOMI, PERRL, no mucositis or oral lesions noted
<li>Neck: Supple,shotty lymphdenopathy, JVP ~8cm
<li>Lungs: Clear to auscultation bilaterally. No wheezes/rhonchi/rales.
<li>Cardiac: Regular rate and rhythm. No murmurs, rubs or gallops. 
<li>Abdomen: Soft, non-tender, non-distended. Normo-active bowel sounds. No organomegaly or masses noted
<li>Rectal: No perirectal abscess or lesions
<li>Extremities: No clubbing, cyanosis, edema. 2+ DP pulses.
<li>Neuro: Alert and oriented. Grossly non-focal. Conversant, moving all extremities. No overt cerebellar signs / incoordination.
<li>Skin: No rashes or lesions noted.
<li>Lines: R arm PICC line without surrounding erythema, drainage, or tenderness
 </ul>');

 /* State transitions */
 /* Initial -Abx-> */
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values  (5000, 5000, 5001, 44391, 'Appropriate antibiotics improve patient condition - Zosyn (pip/tazo)'),
           (5010, 5000, 5001, 44252, 'Appropriate antibiotics improve patient condition - Zosyn (pip/tazo) (alternate)'),
           (5020, 5000, 5001, 44008, 'Appropriate antibiotics improve patient condition - Meropenem'),
           (5030, 5000, 5001, 36210, 'Appropriate antibiotics improve patient condition - Cefepime'),
           (5040, 5000, 5001, 44678, 'Appropriate antibiotics improve patient condition - Aztreonam'),
           (5050, 5000, 5001, 44637, 'Appropriate antibiotics improve patient condition - Ceftazadime');

 /* Initial -IVF->  */
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values (5100, 5000, 5002, 44198, 'IV Fluid resuscitation improves patient condition - Sodium Chloride/Normal Saline'),
          (5110, 5000, 5002, 44439, 'IV Fluid resuscitation improves patient condition - Lactated Ringers'),
          (5120, 5000, 5002, 44290, 'IV Fluid resuscitation improves patient condition - Lactated Ringers v2');

 /* +Abx -IVF-> Treatment Complete */
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values (5210, 5001, 5003, 44198, 'IV Fluid resuscitation improves patient condition - Sodium Chloride/Normal Saline'),
          (5220, 5001, 5003, 44439, 'IV Fluid resuscitation improves patient condition - Lactated Ringers'),
          (5230, 5001, 5003, 44290, 'IV Fluid resuscitation improves patient condition - Lactated Ringers v2');

 /* +IVF -Abx-> Treatment Complete */
 insert into sim_state_transition(sim_state_transition_id, pre_state_id, post_state_id, clinical_item_id, description)
   values  (5300, 5002, 5003, 44391, 'Appropriate antibiotics improve patient condition - Zosyn (pip/tazo)'),
           (5310, 5002, 5003, 44252, 'Appropriate antibiotics improve patient condition - Zosyn (pip/tazo) (alternate)'),
           (5320, 5002, 5003, 44008, 'Appropriate antibiotics improve patient condition - Meropenem'),
           (5330, 5002, 5003, 36210, 'Appropriate antibiotics improve patient condition - Cefepime'),
           (5340, 5002, 5003, 44678, 'Appropriate antibiotics improve patient condition - Aztreonam'),
           (5350, 5002, 5003, 44637, 'Appropriate antibiotics improve patient condition - Ceftazadime');
 
/**** This is getting too painful. We'll just edit directly into pgAdmin datatables and save as part of the core dump files
 insert into sim_state_result(sim_state_result_id, sim_state_id, sim_result_id, clinical_item_id, num_value, text_value, result_flag)
  values (408, 5000, 13210, null, 1, 'Normal');

          (5111, 5000, 13410, 66407,  6.7, 0.2   
          (5111, 5000, 10,    null,   102, 1   High
          (5111, 5000, 20,    null,   128, 5   High
          (5111, 5000, 50,    null,   25,  2   High
          (5111, 5000, 13420, 66159,  480, 13    High
          (5111, 5000, 13502, 69841,  4.4, 0.1   High
          (5111, 5000, 13506, 66505,  3.3, 0.2   High
          (5111, 5000, 16100, 66502,  3.4, 0.2   High
          (5111, 5000, 1000173, 70921, 3.4, 0.1   High
          (5111, 5000, 30,    null,   86,  4   Low
          (5111, 5000, 40,    null, 43,  3   Low
          (5111, 5000, 11000, 66630, 0.8, 0   Low
          (5111, 5000, 11010, 66124, 11.1,  0.3   Low
          (5111, 5000, 11020, 66123, 33,  1   Low
          (5111, 5000, 11030, 66258, 95,  10    Low
          (5111, 5000, 11120,   10,  0,   Low
          (5111, 5000, 11130,   90,  0,   Low
          (5111, 5000, 11220, 66684, 80,  0   Low
          (5111, 5000, 11240, 72951, 720, 0   Low
          (5111, 5000, 13040, 66403, 19,  1   Low
          (5111, 5000, 15010, 66383, 7.34,  0.01    Low
          (5111, 5000, 15020, 66375, 34,  1   Low
          (5111, 5000, 15050, 66392, 7.34,  0.01    Low
          (5111, 5000, 15060, 66495, 34,  1   Low
          (5111, 5000, 16010, 66413, 7.34,  0.01    Low
          (5111, 5000, 16020, 66203, 34,  1   Low
          (5111, 5000, 16060, 66504, 7.34,  0.01    Low
          (5111, 5000, 16070, 66493, 34,  1   Low
****/