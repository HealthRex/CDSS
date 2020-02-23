import pandas as pd
import os
import argparse


from UtilityModel import UtilityModel 
from cost_analysis import compute_alg_covered_flag, get_presciption_profile

parser = argparse.ArgumentParser()
parser.add_argument('--n_vanc_mero', type=int, required=True)
parser.add_argument('--n_mero', type=int, required=True)
parser.add_argument('--n_vanc_piptazo', type=int, required=True)
parser.add_argument('--n_vanc_cefepime', type=int, required=True)
parser.add_argument('--n_vanc_ceftriaxone', type=int, required=True)
parser.add_argument('--n_vanc', type=int, required=True)
parser.add_argument('--n_piptazo', type=int, required=True)
parser.add_argument('--n_cefepime', type=int, required=True)
parser.add_argument('--n_ceftriaxone', type=int, required=True)
parser.add_argument('--out_path', type=str, required=True)


args = parser.parse_args()

data = pd.read_csv('./data/labels_with_probs.csv')

n = {}
n['vancomycin meropenem'] = args.n_vanc_mero
n['vancomycin piperacillin-tazobactam'] = args.n_vanc_piptazo
n['vancomycin'] = args.n_vanc
n['piperacillin-tazobactam'] = args.n_piptazo
n['cefepime'] = args.n_cefepime
n['ceftriaxone'] = args.n_ceftriaxone
n['cefazolin'] = 0
n['vancomycin cefepime'] = args.n_vanc_cefepime
n['vancomycin ceftriaxone'] = args.n_vanc_ceftriaxone
n['meropenem'] = args.n_mero

fpath = './data/model_util_vals.txt'


with open(fpath, 'r') as f:
	lines = f.readlines()

utility_vals = [u.split(',')[1] for u in lines]

umodel = UtilityModel(data,
					  C_meropenem = utility_vals[0],
                      C_vancomycin = utility_vals[1],
                      C_piptazo = utility_vals[2],
                      C_cefepime = utility_vals[3],
                      C_ceftriaxone = utility_vals[4],
                      C_cefazolin = utility_vals[5],
                      C_vanc_meropenem = utility_vals[6],
                      C_vanc_piptazo = utility_vals[7],
                      C_vanc_cefepime = utility_vals[8],
                      C_vanc_ceftriaxone = utility_vals[9])


data = umodel.fit_drug_parameters
profile = get_presciption_profile(data)

f_u_params = os.path.join(args.outpath, 'utility_params.txt')
f_profile = os.path.join(args.outpath, 'profile.csv')

profile.to_csv(f_profile, index=None)

with open(args.outpath, 'w') as w:
	for key in umodel.drug_cost:
	    w.write("%s,%.2f\n" % (key, umodel.drug_cost[key]))


data['alg_covered'] = data.apply(compute_alg_covered_flag, axis=1)
print("Number of mismatches %d" % len(data[data['alg_covered'] == 0]))

