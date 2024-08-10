import pandas as pd
import os
os.chdir('/Users/grolleau/Desktop/github repos/CDSS/scripts/cost_variability_2024/')

def res_fold(to_res, out):
    return [i for i in os.listdir(to_res) if i.startswith(f'res_{out}')][0]

class comb_tab:
    def __init__(self, to_res, comp):
        self.comp = comp
        self.to_res = to_res
        self.folder = {'hi': f'{to_res}/{res_fold(to_res, 'hi')}/{self.comp}', 'lo': f'{to_res}/{res_fold(to_res, 'lo')}/{self.comp}'}
        self.file_names_hi = os.listdir(self.folder['hi'])
        self.file_names_lo = os.listdir(self.folder['lo'])

    def combine(self, var = 'pval'):
        dfs = []
        for file_name in self.file_names_hi:
            for out in ['hi', 'lo']:
                drg_no = ''.join([char for char in file_name if char.isdigit()])   
                df = pd.read_csv(os.path.join(self.folder[out], file_name))
                df['drg_no'] = drg_no
                df['outlier'] = out
                dfs.append(df)
        if var == 'pval':
            self.df = pd.concat(dfs).sort_values(by='fisher_pval', ascending=True)
        elif var == 'or':
            self.df = pd.concat(dfs).sort_values(by='odds_ratio', ascending=False)
        
    def export(self):
        if not os.path.exists('scripts/pipeline/res/res_comb'):
            os.makedirs(f'{self.to_res}/res_comb')
        self.df.to_csv(f'{self.to_res}/res_comb/res_{self.comp}.csv', index=False)

comp_list = ['comp_medorderset', 'comp_proc', 'comp_diag', 'comp_procorderset', 'comp_med']
for comp in comp_list:
    comb = comb_tab('scripts/pipeline/res', comp)
    comb.combine(var = 'pval')
    comb.export()