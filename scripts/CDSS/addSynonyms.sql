-- Add common synonyms to major clinical items, primarily to facilitate user interface simulation order searches by name

update clinical_item
set description = description || ' [CXR]'
where description ~* '^xr.*chest';


update clinical_item
set description = description || ' [BMP]'
where name = 'LABMETB';


update clinical_item
set description = description || ' [CMP]'
where name = 'LABMETC';

update clinical_item
set description = description || ' [LFT]'
where name = 'LABHFP';

update clinical_item
set description = description || ' [EKG]'
where name = 'EKG5';

update clinical_item
set description = description || ' [PT/INR]'
where name = 'LABPT';

update clinical_item
set description = description || ' [UA]'
where description ~* 'urinalysis';

update clinical_item
set description = description || ' [NS IVF][Normal Saline]'
where name = 'RXCUI9863'
and description ~* 'intravenous';

update clinical_item
set description = description || ' [ABG]'
where description ~* 'blood gas'
and description ~* 'arteria'
and name ~* '^LAB|^POC';

update clinical_item
set description = description || ' [VBG]'
where description ~* 'blood gas'
and description ~* 'venous'
and name ~* '^LAB|^POC';

update clinical_item
set description = description || ' [LR][Lactated Ringer]'
where description ~* 'lactate.*intraven';

update clinical_item
set description = description || ' [RBC]'
where description ~* 'red blood cell'
and name not like 'ICD%';

update clinical_item
set description = description || ' [PLT]'
where description ~* 'platelet'
and description not like '%PLT%';

update clinical_item
set description = description || ' [FFP]'
where description ~* 'fresh frozen plasma';
