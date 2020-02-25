update lpch.clinical_note_meta
set FILING_DATE_JITTERED_UTC = case FILING_DATE_JITTERED when null then null else datetime(timestamp(FILING_DATE_JITTERED), 'America/Los_Angeles') end
where true;
