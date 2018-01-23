#!/usr/bin/env python
"""
Test input and output for EventDigraph.
"""

from medinfo.db import DBUtil

# { 'test_db_table' : 'test_data' }
ED_TEST_INPUT_TABLES = {
    'clinical_item_category' :
        "clinical_item_category_id\tsource_table\tdescription\n\
        -100\tTestTable\tTest Category 1\n\
        -200\tTestTable\tTest Category 2\n\
        -300\tTestTable\tTest Category 3\n\
        -400\tTestTable\tTest Category 4\n\
        -500\tTestTable\tTest Category 5\n",
    'clinical_item' :
        "clinical_item_id\tname\tdescription\tclinical_item_category_id\n\
        -100\tTest Item 100\tTest Item 100\t-100\n\
        -200\tTest Item 200\tTest Item 200\t-100\n\
        -300\tTest Item 300\tTest Item 300\t-200\n\
        -400\tTest Item 400\tTest Item 400\t-200\n\
        -500\tTest Item 500\tTest Item 500\t-300\n\
        -600\tTest Item 600\tTest Item 600\t-300\n\
        -700\tTest Item 700\tTest Item 700\t-400\n\
        -800\tTest Item 800\tTest Item 800\t-400\n\
        -900\tTest Item 900\tTest Item 900\t-500\n\
        -1000\tTest Item 1000\tTest Item 1000\t-500\n",
    'patient_item' :
        "patient_item_id\tpatient_id\tclinical_item_id\titem_date\n\
        -100\t-123\t-1000\t1/6/2113 10:20\n\
        -200\t-234\t-900\t2/6/2113 11:20\n\
        -300\t-345\t-800\t3/7/2113 11:20\n\
        -400\t-123\t-1000\t4/6/2113 10:20\n\
        -500\t-234\t-900\t5/6/2113 11:20\n\
        -600\t-345\t-800\t6/6/2113 12:40\n\
        -700\t-456\t-700\t7/7/2113 12:40\n\
        -800\t-123\t-600\t8/8/2113 12:40\n\
        -900\t-234\t-900\t9/9/2113 12:40\n\
        -1000\t-345\t-800\t10/10/2113 12:40\n\
        -1100\t-456\t-700\t11/11/2113 12:40\n\
        -1200\t-567\t-600\t12/12/2113 12:40\n\
        -1300\t-678\t-500\t1/13/2114 12:40\n\
        -1400\t-789\t-400\t2/14/2114 12:40\n\
        -1500\t-789\t-300\t3/15/2114 12:40\n\
        -1600\t-678\t-200\t4/16/2114 12:40\n\
        -1700\t-567\t-500\t5/17/2114 12:40\n\
        -1800\t-456\t-300\t6/18/2114 12:40\n\
        -1900\t-345\t-400\t7/19/2114 12:40\n\
        -2000\t-567\t-100\t8/20/2114 12:40\n"
}

# { 'test_function_name' : { 'test_assertion' : 'test_output' } }
ED_TEST_OUTPUT_TABLES = {
    'test_init' : {
        'category_nodes' : [
            ('Test Category 1', {'count': 2}),
            ('Test Category 2', {'count': 4}),
            ('Test Category 3', {'count': 4}),
            ('Test Category 4', {'count': 5}),
            ('Test Category 5', {'count': 5})
        ],
        'category_edges' : [
            (('Test Category 2', 'Test Category 2'), {'count': 1}),
            (('Test Category 3', 'Test Category 1'), {'count': 2}),
            (('Test Category 3', 'Test Category 3'), {'count': 1}),
            (('Test Category 4', 'Test Category 2'), {'count': 2}),
            (('Test Category 4', 'Test Category 4'), {'count': 3}),
            (('Test Category 5', 'Test Category 3'), {'count': 1}),
            (('Test Category 5', 'Test Category 5'), {'count': 3})
        ],
        'item_nodes' : [
            ('Test Item 100', {'count': 1}),
            ('Test Item 1000', {'count': 2}),
            ('Test Item 200', {'count': 1}),
            ('Test Item 300', {'count': 2}),
            ('Test Item 400', {'count': 2}),
            ('Test Item 500', {'count': 2}),
            ('Test Item 600', {'count': 2}),
            ('Test Item 700', {'count': 2}),
            ('Test Item 800', {'count': 3}),
            ('Test Item 900', {'count': 3})
        ],
        'item_edges' : [
            (('Test Item 1000', 'Test Item 1000'), {'count': 1}),
            (('Test Item 1000', 'Test Item 600'), {'count': 1}),
            (('Test Item 400', 'Test Item 300'), {'count': 1}),
            (('Test Item 500', 'Test Item 100'), {'count': 1}),
            (('Test Item 500', 'Test Item 200'), {'count': 1}),
            (('Test Item 600', 'Test Item 500'), {'count': 1}),
            (('Test Item 700', 'Test Item 300'), {'count': 1}),
            (('Test Item 700', 'Test Item 700'), {'count': 1}),
            (('Test Item 800', 'Test Item 400'), {'count': 1}),
            (('Test Item 800', 'Test Item 800'), {'count': 2}),
            (('Test Item 900', 'Test Item 900'), {'count': 2})


        ]
    }
}
