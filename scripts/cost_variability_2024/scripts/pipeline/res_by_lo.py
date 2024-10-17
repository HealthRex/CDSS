import os
import pandas as pd

def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

drgs = pd.read_csv("/Users/grolleau/Desktop/github repos/CDSS/scripts/cost_variability_2024/tables/drg_to_name.csv", index_col=0)
drg_dic = drgs.to_dict()['drg_name']

for i in os.listdir("res_01_08/res_comb"):
    df = pd.read_csv(f"res_01_08/res_comb/{i}")
    df = df[df['outlier'] == 'lo'] # keep only the rows where the outlier is 'lo'
    df.sort_values("odds_ratio", ascending=False, inplace=True)
    df["drg"] = list(map(lambda x: drg_dic.get(x, 'not found'), df["drg_no"]))
    make_folder("res_or/res_comb_lo")
    df.to_csv(f"res_or/res_comb_lo/{i}", index=False)
    
for i in os.listdir("res_01_08/res_comb"):
    df = pd.read_csv(f"res_01_08/res_comb/{i}")
    df = df[df['outlier'] == 'lo'] # keep only the rows where the outlier is 'lo'
    df["drg"] = list(map(lambda x: drg_dic.get(x, 'not found'), df["drg_no"]))
    make_folder("res_p/res_comb_lo")
    df.to_csv(f"res_p/res_comb_lo/{i}", index=False)