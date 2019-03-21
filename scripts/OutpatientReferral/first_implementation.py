
'''
Goal:
In the test set, what is the precision@5 recommendations?

Data:
2016, New Patient Visit

Features:
Only 1 feature: Referral.

Methods:
Referral -> Most associated Specialty -> top 5 orders

Metrics:
precision@5 recommendations
'''

import pandas as pd
pd.set_option('display.width', 1000)


'''
Load data that were previously prepared?


Question: What is the "ground truth"?
Detailedly: For each referral, what are the actual "upcoming orders"?

This question seems not the most valid, because:
- When a primary care doctor gives a referral, the doctor should already know
which specialty that should be. So our task should not be "predicting specialty"

- However, this 'specialty' info is not in EMR. We have to statistically find
which specialties are associated with referral. (why though? sanity check?)

- Essentially, want to find which specialty leads to which tests.
    - Even better, adding in patient info upon prior referral?
    - Seems like need to reformulate the problem to focus on specialty, instead of referral!
'''


'''
Next steps:
(1) First implementation, check the top 10 recommendations given the specialty of any department 
(only 1 feature).
(2) Second implementation, check if adding in patient info (N features) upon the referral (will 
need backtrace in time to see which earlier referral leads to this specialty consultation) will 
improve the performance.
'''
