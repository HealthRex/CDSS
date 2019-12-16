class UtilityModel():
    
    def __init__(self, C_no_cover=-100, C_meropenem=-1, C_vancomycin=-1,
                 C_piptazo=-1, C_cefepime=-1, C_ceftriaxone=-1,
                 C_cefazolin=-1):
        
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
    
    
    