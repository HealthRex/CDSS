import pandas as pd

def collapse_labels(arr):
    """If anything in arr is 3 (ie contradiction encountered in labelling function),
         then label is unknown -1.
       else If anything in arr is -1, label is unknown -1
       Else if anything in arr is 0, label is 0
       Else label is 1
    """
    three_detected = False
    unk_detected = False
    zero_detected = False
    for val in arr:
        if val == 3:
            three_detected = True
        elif val == -1:
            unk_detected = True
        elif val == 0:
            zero_detected = True
    
    if three_detected or unk_detected:
        return -1
    elif zero_detected:
        return 0
    else:
        return 1
    
def collapse_organism(arr):
    x = []
    for a in arr:
        if isinstance(a, str):
            x.append(a)
        else:
            x.append('Nothing')
    return ' '.join(x)
    


if __name__ == '__main__':
    # Read in cohort
    df_cohort = pd.read_csv('./data/er_empiric_treatment.csv')

    df_cohort[['cefazolin',
               'ceftriaxone',
               'vancomycin',
               'cefepime', 
               'piptazo', 
               'meropenem']] = df_cohort[['cefazolin',
                                          'ceftriaxone', 
                                          'vancomycin',
                                          'cefepime',
                                          'piptazo',
                                          'meropenem']].fillna(1.0)

    # Collapse labels - we want one label per drug per encounter
    labels = df_cohort[['pat_enc_csn_id_coded', 'organism',
              'cefazolin', 'ceftriaxone',
              'vancomycin', 'cefepime',
              'piptazo', 'meropenem']].sort_values('organism').groupby(
             'pat_enc_csn_id_coded').agg({
             'cefazolin' : collapse_labels,
             'ceftriaxone' : collapse_labels,
             'cefepime' : collapse_labels,
             'piptazo' : collapse_labels,
             'vancomycin' : collapse_labels,
             'meropenem' : collapse_labels,
             'organism' : collapse_organism
         }).reset_index()

    # Only keep samples where we know each label - one of the biggest 
    # limitations in this study.... 
    labels_small =        labels[(labels['cefazolin'] != -1) & \
                             (labels['ceftriaxone'] != -1) & \
                             (labels['cefepime'] != -1) & \
                             (labels['piptazo'] != -1) & \
                             (labels['vancomycin'] != -1) & \
                             (labels['meropenem'] != -1)]

    # Merge labels_small back onto data
    df_cohort = df_cohort.drop(['cefazolin', 'ceftriaxone', 'vancomycin',
                      'cefepime', 'piptazo', 'meropenem', 'organism'], axis=1)

    df_cohort = pd.merge(df_cohort,
                          labels_small, 
                          on='pat_enc_csn_id_coded', 
                          how='inner').groupby(
                            'pat_enc_csn_id_coded').first().reset_index()

    # Create combo labels
    df_cohort['vanc_meropenem'] = df_cohort.apply(
        lambda x: 1 if x.vancomycin == 1 or x.meropenem == 1 else 0, axis=1)
    df_cohort['vanc_piptazo'] = df_cohort.apply(
        lambda x: 1 if x.vancomycin == 1 or x.piptazo == 1 else 0, axis=1)
    df_cohort['vanc_cefepime'] = df_cohort.apply(
        lambda x: 1 if x.vancomycin == 1 or x.cefepime == 1 else 0, axis=1)
    df_cohort['vanc_ceftriaxone'] = df_cohort.apply(
        lambda x: 1 if x.vancomycin == 1 or x.ceftriaxone == 1 else 0, axis=1)


    df_cohort.to_csv('./data/labels.csv', index=None)
