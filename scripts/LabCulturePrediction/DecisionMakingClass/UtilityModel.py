from scipy.optimize import broyden1
import numpy as np
import pdb

class UtilityModel():
    
    def __init__(self, data, C_no_cover=-100, C_meropenem=-1, C_vancomycin=-1,
                 C_piptazo=-1, C_cefepime=-1, C_ceftriaxone=-1,
                 C_cefazolin=-1):
        self.data = data

        self.C_no_cover = C_no_cover
        self.drug_cost = {}
        self.drug_cost['meropenem'] = C_meropenem
        self.drug_cost['vancomycin'] = C_vancomycin
        self.drug_cost['piptazo'] = C_piptazo
        self.drug_cost['cefepime'] = C_cefepime
        self.drug_cost['ceftriaxone'] = C_ceftriaxone
        self.drug_cost['cefazolin'] =  C_cefazolin
        
        self.drug_cost['vanc_meropenem'] = C_vancomycin + C_meropenem
        self.drug_cost['vanc_piptazo'] = C_vancomycin + C_piptazo
        self.drug_cost['vanc_cefepime'] = C_vancomycin + C_cefepime
        self.drug_cost['vanc_ceftriaxone'] = C_vancomycin + C_ceftriaxone
    
    
    def compute_best_action(self, x):
        """ 
        Given model outputs and utility values, return the optimal
        treatment based on expected utility.
        """

        drugs = ['cefazolin', 'ceftriaxone', 'cefepime', 
                 'piptazo', 'vancomycin', 'vanc_ceftriaxone',
                 'vanc_cefepime', 'vanc_piptazo',
                 'meropenem', 'vanc_meropenem']

        drugs.reverse() # Looks at broadest spectrum first
        
        best_drug = None
        EU_best = -99999999
        for drug in drugs:
            EU = (1-x["p_of_c_"+drug])*(self.C_no_cover + self.drug_cost[drug]) + \
                      x["p_of_c_"+drug] * self.drug_cost[drug]
            if EU > EU_best:
                EU_best = EU
                best_drug = drug
                
        if best_drug == 'vanc_meropenem':
            best_drug = 'vancomycin meropenem'
        if best_drug == 'vanc_piptazo':
            best_drug = 'vancomycin piperacillin-tazobactam'
        if best_drug == 'vanc_cefepime':
            best_drug = 'vancomycin cefepime'
        if best_drug == 'vanc_ceftriaxone':
            best_drug = 'vancomycin ceftriaxone'
        if best_drug == 'piptazo':
            best_drug = 'piperacillin-tazobactam'
        return best_drug

    def f(self, vars):
        C_meropenem, C_vancomycin, C_piptazo, C_cefepime, C_ceftriaxone, C_cefazolin = vars
        equations = []
        drugs = ['cefazolin', 'ceftriaxone', 'cefepime', 
             'piptazo', 'vancomycin', 'meropenem']
        relative_ns = np.array([0, 0, 8, 6, 4, 0])
        p_res = 1 - self.data[['p_of_c_' + t for t in drugs]].values
        for i, drug in enumerate(drugs):
          eq = np.sum([1 if np.argmax(p_res[j, :] * -100 + np.asarray([C_meropenem,
                                                                 C_vancomycin,
                                                                 C_piptazo,
                                                                 C_cefepime,
                                                                 C_ceftriaxone,
                                                                 C_cefazolin]))
                  == i else 0 for j in range(p_res.shape[0])]) - relative_ns[i]

          if i != 5:
              equations.append(eq)

        equations.append(C_meropenem + C_vancomycin + C_piptazo + C_cefepime + C_ceftriaxone + C_cefazolin)
        
        return equations
    # def _generate_equations(self, data,
    #                         n_meropenem,
    #                         n_vanc,
    #                         n_piptazo,
    #                         n_cefepime,
    #                         n_ceftriaxone,
    #                         n_cefazolin):

    #     equations = [] 
    #     single_drugs = ['cefazolin', 'ceftriaxone', 'cefepime', 
    #              'piptazo', 'vancomycin', 'meropenem']

    #     treatments = ['cefazolin', 'ceftriaxone', 'cefepime', 
    #                   'piptazo', 'vancomycin', 'vanc_ceftriaxone',
    #                   'vanc_cefepime', 'vanc_piptazo',
    #                   'meropenem', 'vanc_meropenem']


    #     for drug in single_drugs:
    #         p_res = 1 - data[['p_of_c_' + t for t in single_drugs]].values
    #         np.sum([1 if np.argmax(pres[j, :] * -100 + C_)])



    def fit_drug_parameters(self,
                            n_meropenem=-2,
                            n_vanc=-2,
                            n_piptazo=-2,
                            n_cefepime=-2,
                            n_ceftriaxone=-2,
                            n_cefazolin=-2):
        """ This function solves a system of equations to fit cost values
            for each of the six antibiotics. 
        """

        test = tuple([n_meropenem,
                         n_vanc,
                         n_piptazo,
                         n_cefepime,
                         n_ceftriaxone,
                         n_cefazolin])
        pdb.set_trace()


        drug_costs = broyden1(self.f, (self.drug_cost['meropenem'],
                                        self.drug_cost['vancomycin'],
                                        self.drug_cost['piptazo'],
                                        self.drug_cost['cefepime'],
                                        self.drug_cost['ceftriaxone'],
                                        self.drug_cost['cefazolin']))
        pdb.set_trace()
        # self.C_meropenem = drug_costs[0]
        # self.C_vancomycin = drug_costs[1]
        # self.C_piptazo = drug_costs[2]
        # self.C_cefepime = drug_costs[3]
        # self.C_ceftriaxone = drug_costs[4]
        # self.C_cefazolin = drug_costs[5]


