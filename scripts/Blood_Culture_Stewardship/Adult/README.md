# Here are the codes for Blood Culture Stewardship Adult cohort.
- BloodCultStewardshipCohort_Creation_StructureEHR.ipynb contains code for create adult study cohort
- BloodCultStewardship-AddingEDNotes.ipynb Extracts ED provider Notes for study cohort
- ModelDevelopment_StructuredEHRData_LR.ipynb Logstic Regression model for prediction
- ModelDevelopment_StructuredEHRData_PointingSystem.ipynb Pointing based system retrived from LR model
- Extract_Relevent_Chunk.ipynb Chunk notes to get embeding representation to extract most relevent chunks
- Fit_Notes_LLM_BloodCulture_Classification_NoFabre.ipynb Use Secure Stanford GPT-4 and ask to classify patient for likelihood of posetive blood culture (No fabre framework)
- Fit_Notes_LLM_BloodCulture_Classification_NoFabre-COT.ipynb The same experiment as the last note book here i just check what if we asked the LLM to highlight it's reason for labeling
- Notes_With_EHR_LLM_Classification.ipynb Adding EHR data
- Apply_Fabre_Fit_Notes_LLM.ipynb using Fabre zero shot learning, EHR included in prompt
