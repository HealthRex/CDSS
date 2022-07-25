import pdb
import argparse
import sys
import os
import utils.create_metadata as comp_pt_nums
import logging

sys.path.append(os.getcwd())
parser = argparse.ArgumentParser()

# pdb.set_trace()
client_name ="som-nero-phi-jonc101-secure"
patient_id = 'anon_id'
query_demog = "select * from `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_demographic`"
comp_pt_nums.compute_paients_demog(client_name
									, patient_id
									, query_demog)
