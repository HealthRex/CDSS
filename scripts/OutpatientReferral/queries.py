

from medinfo.db.Model import SQLQuery

ENCOUNTER_TABLE = 'datalake_47618.encounter'
ORDERPROC_TABLE = 'datalake_47618.order_proc'
DIAGNOSIS_TABLE = 'datalake_47618.diagnosis_code'
DEPMAP_TABLE = 'datalake_47618.dep_map'

def query_sample():
    return """
            select patient_item_id, external_id, clinical_item_id, item_date, encounter_id, text_value, num_value, source_id 
            from 
            `clinical_inpatient.patient_item` 
            where item_date >= timestamp('2014-01-01 00:00:00')
            """

def query_for_recent6months():
    query = SQLQuery()
    query.addSelect('p1.pat_enc_csn_id_coded AS referral_enc_id')
    query.addSelect('p1.description AS referral_name')
    query.addSelect('e1.appt_when_jittered AS referral_time')
    query.addSelect('e1.jc_uid AS pat_id')
    query.addSelect('d1.icd9 AS referral_icd9')
    query.addSelect('d1.icd10 AS referral_icd10')

    query.addSelect('p2.pat_enc_csn_id_coded AS specialty_enc_id')
    query.addSelect('e2.appt_when_jittered AS specialty_time')
    query.addSelect('d2.department_name AS specialty_dep')
    query.addSelect('d2.specialty AS specialty_name')
    query.addSelect('p2.description AS specialty_order')

    query.addFrom('%s AS e1' % ENCOUNTER_TABLE)
    query.addFrom('%s AS p1' % ORDERPROC_TABLE)
    query.addFrom('%s AS d1' % DIAGNOSIS_TABLE)

    query.addFrom('%s AS e2' % ENCOUNTER_TABLE)
    query.addFrom('%s AS p2' % ORDERPROC_TABLE)
    query.addFrom('%s AS d2' % DEPMAP_TABLE)

    query.addWhere("lower(p1.description) like '%referral%'")
    query.addWhere("p1.pat_enc_csn_id_coded = e1.pat_enc_csn_id_coded")
    query.addWhere("p1.pat_enc_csn_id_coded = d1.pat_enc_csn_id_coded")
    query.addWhere("e1.appt_when_jittered >= '2016-01-01'")
    query.addWhere("e1.appt_when_jittered < '2017-01-01'")

    query.addWhere("e1.jc_uid = e2.jc_uid")
    query.addWhere("e1.pat_enc_csn_id_coded != e2.pat_enc_csn_id_coded")
    query.addWhere("e1.appt_when_jittered <= e2.appt_when_jittered")
    query.addWhere("DATE_ADD(date(timestamp(e1.appt_when_jittered)), INTERVAL 6 month) > date(timestamp(e2.appt_when_jittered))")

    query.addWhere("e2.visit_type like '%NEW PATIENT%'")
    query.addWhere("e2.department_id = d2.department_id")
    query.addWhere("p2.pat_enc_csn_id_coded = e2.pat_enc_csn_id_coded")
    return str(query)