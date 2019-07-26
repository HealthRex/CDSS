#!/usr/bin/env python
from medinfo.dataconv_starr.STARRDemographicsConversion import STARRDemographicsConversion

'''
setup credentials: export GOOGLE_APPLICATION_CREDENTIALS='<path to json>'
'''

if __name__ == '__main__':
    STARR_demo_conv = STARRDemographicsConversion()
    print('testing')
    #STARR_demo_conv.querySourceItems(patientIds=['JCcdf815', 'JCe99f38', 'JCea259c'], debug=True)

    STARR_demo_conv.convertSourceItems(['JCcdf815', 'JCe99f38', 'JCea259c'])
    print('done')
