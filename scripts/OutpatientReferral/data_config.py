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