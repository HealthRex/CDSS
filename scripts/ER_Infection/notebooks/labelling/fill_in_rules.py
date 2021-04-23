import pandas as pd
import numpy as np
import os 

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ccorbin/.config/gcloud/application_default_credentials.json' 
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101' 

from google.cloud import bigquery
client=bigquery.Client()


def fill_in_cefazolin(x):
    
    # If not missing just return what it is. 
    if x.Cefazolin == 'Susceptible' or x.Cefazolin == 'Resistant':
        return x.Cefazolin
    
    # Read in bug rules
    df_bug_rules = pd.read_csv('Bacteria_AST_Rules.csv')
    r_bugs = set(df_bug_rules.query("cefazolin_r == 1")['Organism'].values)
    s_bugs = set(df_bug_rules.query("cefazolin_s == 1")['Organism'].values)
    
    # Uses hand labelled list of resistant bugs
    if x.organism in r_bugs:
        return "Resistant"
    
    # Uses hand labelled always susceptible bugs
    if x.organism in s_bugs:
        return "Susceptible"

    # For anything STREPTOCOCCUS related except STREPTOCOCCUS PNEUMONIAE  - refer to penicillin 
    if ('STREPTOCOCCUS' in x.organism or 'STREPTOCOCCI' in x.organism) and x.organism != 'STREPTOCOCCUS PNEUMONIAE':
        if x.Penicillin is not None:
            return x.Penicillin
    
    # Check For MRSA in STAPH AUREUS 
    if x.organism == 'STAPHYLOCOCCUS AUREUS':
        if x.Oxacillin is not None:
            return x.Oxacillin 
        
    # If anything resistant to Cefepime or Ceftriaxone, assume resistant to Cefazolin
    if x.Cefepime == "Resistant" or x.Ceftriaxone == 'Resistant':
        return "Resistant"
    
    # Will apply Nancy Watz Rule Later (assume susc if not listed)
    return "Susceptible"

def fill_in_ceftriaxone(x):
    
    # If not missing just return what it is. 
    if x.Ceftriaxone == 'Susceptible' or x.Ceftriaxone == 'Resistant':
        return x.Ceftriaxone
    
    # Read in bug rules
    df_bug_rules = pd.read_csv('Bacteria_AST_Rules.csv')
    r_bugs = set(df_bug_rules.query("ceftriaxone_r == 1")['Organism'].values)
    s_bugs = set(df_bug_rules.query("ceftriaxone_s == 1")['Organism'].values)
    
    # Uses hand labelled list of resistant bugs
    if x.organism in r_bugs:
        return "Resistant"
    
    # Uses hand labelled always susceptible bugs
    if x.organism in s_bugs:
        return "Susceptible"

    # For anything STREPTOCOCCUS related - refer to penicillin 
    if ('STREPTOCOCCUS' in x.organism or 'STREPTOCOCCI' in x.organism):
        if x.Penicillin is not None:
            return x.Penicillin
        
    # Check For MRSA in STAPH AUREUS 
    if x.organism == 'STAPHYLOCOCCUS AUREUS':
        if x.Oxacillin is not None:
            return x.Oxacillin 

    # If anything resistant to Cefepime, assume resistant to Ceftriaxone
    if x.Cefepime == "Resistant":
        return "Resistant"
    
    # If susceptible to Cefazolin, assume susceptible to Ceftriaxone
    if x.Cefazolin == "Susceptible":
        return "Resistant"
    
    # Will apply Nancy Watz Rule Later (assume susc if not listed)
    return "Susceptible"

def fill_in_cefepime(x):
    
    # If not missing just return what it is. 
    if x.Cefepime == 'Susceptible' or x.Cefepime == 'Resistant':
        return x.Cefepime
    
    # Read in bug rules
    df_bug_rules = pd.read_csv('Bacteria_AST_Rules.csv')
    r_bugs = set(df_bug_rules.query("cefepime_r == 1")['Organism'].values)
    s_bugs = set(df_bug_rules.query("cefepime_s == 1")['Organism'].values)
    
    # Uses hand labelled list of resistant bugs
    if x.organism in r_bugs:
        return "Resistant"
    
    # Uses hand labelled always susceptible bugs
    if x.organism in s_bugs:
        return "Susceptible"

    # For anything STREPTOCOCCUS related - refer to penicillin 
    if ('STREPTOCOCCUS' in x.organism or 'STREPTOCOCCI' in x.organism):
        if x.Penicillin is not None:
            return x.Penicillin
        
    # Check For MRSA in STAPH AUREUS 
    if x.organism == 'STAPHYLOCOCCUS AUREUS':
        if x.Oxacillin is not None:
            return x.Oxacillin 
    
    # If susceptible to Cefazolin or Ceftriaxone assume susceptible to Cefepime
    if x.Cefazolin == "Susceptible" or x.Ceftriaxone == "Susceptible":
        return "Susceptible"
    
    # Will apply Nancy Watz Rule Later (assume susc if not listed)
    return "Susceptible"

def fill_in_zosyn(x):
     
    # If not missing just return what it is. 
    if x.Zosyn == 'Susceptible' or x.Zosyn == 'Resistant':
        return x.Zosyn
    
    # Read in bug rules
    df_bug_rules = pd.read_csv('Bacteria_AST_Rules.csv')
    r_bugs = set(df_bug_rules.query("zosyn_r == 1")['Organism'].values)
    s_bugs = set(df_bug_rules.query("zosyn_s == 1")['Organism'].values)
    
    # Uses hand labelled list of resistant bugs
    if x.organism in r_bugs:
        return "Resistant"
    
    # Uses hand labelled always susceptible bugs
    if x.organism in s_bugs:
        return "Susceptible"
    
    # For anything STREPTOCOCCUS related - refer to penicillin 
    if ('STREPTOCOCCUS' in x.organism or 'STREPTOCOCCI' in x.organism):
        if x.Penicillin is not None:
            return x.Penicillin
        
    # Check For MRSA in STAPH AUREUS 
    if x.organism == 'STAPHYLOCOCCUS AUREUS':
        if x.Oxacillin is not None:
            return x.Oxacillin 
        
    # If susceptible to ampicillin, then zosyn susceptible
    if x.Ampicillin == "Susceptible":
        return x.Ampicillin
    
    # Will apply Nancy Watz Rule Later (assume susc if not listed)
    return "Susceptible"


def fill_in_vancomycin(x):
    # If not missing just return what it is. 
    if x.Vancomycin == 'Susceptible' or x.Vancomycin == 'Resistant':
        return x.Vancomycin
    
    # Read in bug rules
    df_bug_rules = pd.read_csv('Bacteria_AST_Rules.csv')
    r_bugs = set(df_bug_rules.query("vancomycin_r == 1")['Organism'].values) # Want to make sure I catch all gram negative bugs in here
    s_bugs = set(df_bug_rules.query("vancomycin_s == 1")['Organism'].values)
    
    # Uses hand labelled list of resistant bugs
    if x.organism in r_bugs:
        return "Resistant"
    
    # Uses hand labelled always susceptible bugs
    if x.organism in s_bugs:
        return "Susceptible"
    
    
    # Will apply Nancy Watz Rule Later (assume susc if not listed)
    return "Susceptible"

def fill_in_meropenem(x):
    # If not missing just return what it is. 
    if x.Meropenem == 'Susceptible' or x.Meropenem == 'Resistant':
        return x.Meropenem
    
    # Read in bug rules
    df_bug_rules = pd.read_csv('Bacteria_AST_Rules.csv')
    r_bugs = set(df_bug_rules.query("meropenem_r == 1")['Organism'].values) # Want to make sure I catch all gram negative bugs in here
    s_bugs = set(df_bug_rules.query("meropenem_s == 1")['Organism'].values)
    
    # Uses hand labelled list of resistant bugs
    if x.organism in r_bugs:
        return "Resistant"
    
    # Uses hand labelled always susceptible bugs
    if x.organism in s_bugs:
        return "Susceptible"
    
     # Check For MRSA in STAPH AUREUS 
    if x.organism == 'STAPHYLOCOCCUS AUREUS':
        if x.Oxacillin is not None:
            return x.Oxacillin 
        
    # If susceptible to ampicillin, then meropenem susceptible
    if x.Ampicillin == "Susceptible": # not the case with Enteroccocus, but this should be in alwasys resistant list above. 
        return x.Ampicillin
    
    # Will apply Nancy Watz Rule Later (assume susc if not listed)
    return "Susceptible"

def combine_labels(arr):
    """
    Sometimes organisms have multiple suscept labels. When they do, if any of them are not one of
    Susceptible, Positive, or Susceptible - Dose Dependent then we say organism is resistant to 
    said antibiotic
    """
    for a in arr:
        if a not in ['Susceptible', 'Positive', 'Susceptible - Dose Dependent']:
            return 'Resistant'
    return 'Susceptible'

def combine_antibiotic_syns(x):
    """
    Antibiotics often are given different names in the AST tables, this function combines
    synnonyms so that we don't have to refer to multiple names in downstream analysis. 
    """
    if x == 'Aztreonam.':
        return 'Aztreonam'
    elif x == 'Cefazolin..':
        return 'Cefazolin'
    elif x == 'Ceftazidime.':
        return 'Ceftazidime'
    elif x in ('Ceftriaxone (Meningeal)', 'Ceftriaxone (Non-Meningeal)', 'Ceftriaxone.'):
        return 'Ceftriaxone'
    elif x in ('Ciprofloxacin.'):
        return 'Ciprofloxacin'
    elif x == 'Gentamicin 500 mcg/ml.':
        return 'Gentamicin'
    elif x in ('Oxacillin Screen', 'Oxacillin.'):
        return 'Oxacillin'
    elif x in ('PENICILLIN G (MENINGEAL)','PENICILLIN G (NON-MENINGEAL)', 'PENICILLIN V (ORAL)', 'Penicillin..'):
        return 'Penicillin'
    elif x == 'Trimethoprim/Sulfamethoxazole.':
        return 'Trimethoprim/Sulfamethoxazole'
    else:
        return x


if __name__ == '__main__':
    
    # Query positive culture data
    query = """
    SELECT DISTINCT cohort.pat_enc_csn_id_coded, cults.order_proc_id_coded, cs.sens_organism_sid, cs.line, cs.organism, cs.antibiotic, cs.suscept, cs.sensitivity_value, cs.sens_ref_range 
    FROM `mining-clinical-decisions.abx.culture_orders_within_24_hrs` cults
    INNER JOIN `mining-clinical-decisions.abx.interm_cohort_with_no_inf_rules` cohort
    USING (pat_enc_csn_id_coded)
    INNER JOIN `shc_core.culture_sensitivity` cs
    USING (order_proc_id_coded)
    WHERE organism <> "COAG NEGATIVE STAPHYLOCOCCUS"
    AND organism not LIKE "%CANDIDA%"
    AND organism not in ('HAEMOPHILUS INFLUENZAE', 'HAEMOPHILUS PARAINFLUENZAE')
    ORDER BY cohort.pat_enc_csn_id_coded, cults.order_proc_id_coded, cs.line
    """

    query_job = client.query(query)
    df=query_job.to_dataframe()

    # Collapses labels for all unique combinations of csns, order_ids, organism_sids, and organisms
    df[['pat_enc_csn_id_coded', 'order_proc_id_coded', 'sens_organism_sid', 'organism']].fillna(
        99999, inplace=True)
    df = (df
        .assign(example = lambda x: x.pat_enc_csn_id_coded.map(str) + ', ' \
                + x.order_proc_id_coded.map(str) + ', ' + x.sens_organism_sid + ', ' + x.organism,
                antibiotic = lambda x: [combine_antibiotic_syns(a) for a in x.antibiotic])
        .groupby(['example', 'antibiotic']) 
        .agg({'suscept' : lambda x: combine_labels(x)})          
        .reset_index()
    )

    filter_cols = ['example', 'pat_enc_csn_id_coded', 'organism', 'order_proc_id_coded', 'sens_organism_sid',
               'Cefepime', 'Ceftriaxone', 'Cefazolin', 'Vancomycin', 'Meropenem', 'Piperacillin/Tazobactam',
               'Ampicillin', 'Penicillin', 'Oxacillin']

    # Pivot so that we get one column per antibiotic. Each row should be a
    # unique combo of csn, order_id, organims, organism_id
    df_wide = (df
        .pivot(index='example', columns='antibiotic', values='suscept')
        .reset_index()
        .assign(organism = lambda x: [a.split(', ')[3] for a in x.example],
                order_proc_id_coded = lambda x: [a.split(', ')[1] for a in x.example],
                sens_organism_sid = lambda x: [a.split(', ')[2] for a in x.example],
                pat_enc_csn_id_coded = lambda x: [a.split(', ')[0] for a in x.example])
    )[filter_cols]

    # Fill in missing values with set of rules defined in functions above
    df_wide = (df_wide
        .assign(Cefazolin=lambda x: df_wide.apply(lambda x: fill_in_cefazolin(x), axis=1),
                Ceftriaxone=lambda x: df_wide.apply(lambda x: fill_in_ceftriaxone(x), axis=1),
                Cefepime=lambda x: df_wide.apply(lambda x: fill_in_cefepime(x), axis=1),
                Zosyn=lambda x: df_wide.apply(lambda x: fill_in_zosyn(x), axis=1),
                Vancomycin=lambda x: df_wide.apply(lambda x: fill_in_vancomycin(x), axis=1),
                Meropenem=lambda x: df_wide.apply(lambda x: fill_in_meropenem(x), axis=1))
        .groupby('pat_enc_csn_id_coded')
        .agg({'Cefazolin' : lambda x: "Resistant" if any(x == "Resistant") else "Susceptible",
              'Ceftriaxone' : lambda x: "Resistant" if any(x == "Resistant") else "Susceptible",
              'Cefepime' : lambda x: "Resistant" if any(x == "Resistant") else "Susceptible",
              'Zosyn' : lambda x: "Resistant" if any(x == "Resistant") else "Susceptible",
              'Vancomycin' : lambda x: "Resistant" if any(x == "Resistant") else "Susceptible",
              'Meropenem' : lambda x: "Resistant" if any(x == "Resistant") else "Susceptible"})
        .reset_index()
    )

    # Query cohort table and merge to get index time for each csn
    query = """
    SELECT DISTINCT anon_id, pat_enc_csn_id_coded, index_time
    FROM mining-clinical-decisions.abx.interm_cohort_with_no_inf_rules
    """
    query_job =client.query(query)
    df_cohort=query_job.to_dataframe()

    df_wide = (df_wide
        .join(df_cohort, on='pat_enc_csn_id_coded', how='left')
    )

    # Upload table 
    table_schema = [{'name' : 'anon_id', 'type' : 'STRING'},
                    {'name' : 'pat_enc_csn_id_coded', 'type' : 'INTEGER'},
                    {'name' : 'index_time', 'type' : 'TIMESTAMP'},
                    {'name' : 'Cefazolin', 'type' : 'STRING'},
                    {'name' : 'Ceftriaxone', 'type' : 'STRING'},
                    {'name' : 'Cefepime', 'type' : 'STRING'},
                    {'name' : 'Zosyn', 'type' : 'STRING'},
                    {'name' : 'Vancomycin', 'type' : 'STRING'},
                    {'name' : 'Meropenem', 'type' : 'STRING'}]

    DATASET_NAME = 'abx'
    TABLE_NAME = 'final_ast_labels'
    df_wide.to_gbq(destination_table='%s.%s' % (DATASET_NAME, TABLE_NAME),
                   project_id='mining-clinical-decisions',
                   table_schema=table_schema,
                   if_exists='replace')

