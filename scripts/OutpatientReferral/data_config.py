referral_to_specialty_tuples =\
[
    ('REFERRAL TO DERMATOLOGY', 'Dermatology'),
    ('REFERRAL TO GASTROENTEROLOGY', 'Gastroenterology'),
    ('REFERRAL TO EYE', 'Ophthalmology'),
    # REFERRAL TO PAIN CLINIC PROCEDURES,   Pain Management #(cnt: 525, but Neurosurgery has 224)
    ('REFERRAL TO ORTHOPEDICS', 'Orthopedic Surgery'),
    ('REFERRAL TO CARDIOLOGY', 'Cardiology'),
    ('REFERRAL TO PSYCHIATRY', 'Psychiatry'),
    ('SLEEP CLINIC REFERRAL', 'Sleep Center'),
    ('REFERRAL TO ENT/OTOLARYNGOLOGY', 'ENT-Otolaryngology'),  # (cnt: 2170, but Oncology has 480)
    ('REFERRAL TO PAIN CLINIC', 'Pain Management'),
    ('REFERRAL TO UROLOGY CLINIC', 'Urology'),  # (cnt: 2827, but Oncology has 605)
    ('REFERRAL TO ENDOCRINE CLINIC', 'Endocrinology'), # Suggested by Jon Chen
    ('REFERRAL TO HEMATOLOGY', 'Hematology')
]
referral_to_specialty_dict = dict(referral_to_specialty_tuples)

import pandas as pd

def get_icd10_category_mapping():
    df = pd.read_csv('mapping/icd10_categories.csv', keep_default_na=False, header=None)
    icd10_category_mapping = dict(zip(df[0], df[1]))
    return icd10_category_mapping

if __name__ == '__main__':
    print get_icd10_category_mapping()