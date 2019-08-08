#!/usr/bin/env python
'''
setup credentials: export GOOGLE_APPLICATION_CREDENTIALS='<path to json>'
'''

from medinfo.dataconversion.starr_conv.STARRDemographicsConversion import STARRDemographicsConversion
from medinfo.db import DBUtil
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader

TEST_SOURCE_TABLE = 'starr_datalake2018.demographic'

if __name__ == '__main__':
    ClinicalItemDataLoader.build_clinical_item_psql_schemata()
    STARR_demo_conv = STARRDemographicsConversion()
    print('testing')
    #STARR_demo_conv.querySourceItems(patientIds=['JCcdf815', 'JCe99f38', 'JCea259c'], debug=True)

    patientIds = ['JCd5ef6e', 'JCce317d', 'JCe83f82']

    STARR_demo_conv.convertSourceItems(patientIds)

    testQuery = \
        """
        select 
            pi.external_id,
            pi.patient_id,
            pi.encounter_id,
            cic.description,
            ci.external_id,
            ci.name,
            ci.description,
            pi.item_date
        from
            patient_item as pi,
            clinical_item as ci,
            clinical_item_category as cic
        where
            pi.clinical_item_id = ci.clinical_item_id and
            ci.clinical_item_category_id = cic.clinical_item_category_id and
            cic.source_table = '%s'
        order by
            pi.patient_id desc, ci.name
        """ % TEST_SOURCE_TABLE

    actualData = DBUtil.execute(testQuery)
    print(actualData)
    print('done')

