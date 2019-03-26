

(1) In the 1st implementation, try to do:

    referral (freq) -> specialty -> orders

Noise is extremely large. 
Even when achieving a >40% precision@10, the results do not 
make sense. For example:
- referral:REFERRAL TO NEUROGENETICS ONCOLOGY
- specialty:Ophthalmology
- actual_orders:['PROTHROMBIN TIME', 'PTT PARTIAL THROMBOPLASTIN TIME', 'CBC W/O DIFF', 'METABOLIC PANEL, BASIC', 'TYPE AND SCREEN', 'BLOOD TYPE VERIFICATION', 'MR BRAIN COMPLETE SPINE WO IV CONTRAST', 'NO SKIN PREP NEEDED', 'RISK FOR VENOUS THROMBOEMBOLISM - VTE RISK ASSESSMENT', 'NO MECHANICAL VTE PROPHYLAXIS REQUIRED']
- predict_orders:['REFERRAL TO PHYSICAL THERAPY', 'CBC W/O DIFF', 'METABOLIC PANE', 'PROTHROMBIN TIME', 'PTT PARTIAL THROMBOPLASTIN TIME', 'RISK FOR VENOUS THROMBOEMBOLISM - VTE RISK ASSESSMENT', 'REFERRAL TO PAIN CLINIC', 'TYPE AND SCREEN', 'MR BRAIN', 'PERIPHERAL IV INSERTION CARE']

(1.5) Jon Chen's advice:
Account for orders that already happened to the patient before the specialty visit. E.g., 
like a hyperthyroid patient will get a TSH test, so that should be predicted, but specialist 
may skip that test if PCP already did it recently. Should not count algorithm as "wrong" for 
predicting it in that case. Try having two different reference sets for the "correct" y labels. 
- Everything the specialist orders on first visit and 
- Everything ordered by ANYONE between (and including) the PCP referral visit and the first specialty 
visit.

(2) In the 2nd implementation, try to do first:

    specialty -> orders
    
Then integrate into the logic:

    referral (freq) -> specialty -> orders
    referral (dist) -> 
    pat_info        ->
                                 ->