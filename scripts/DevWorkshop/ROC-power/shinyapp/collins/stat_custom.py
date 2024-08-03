import numpy as np

class collins_c:
    def __init__(self, c, p, targ_se):
        self.c = c
        self.p = p
        self.targ_se = targ_se
    
    def se_cal(self, N):
        c = self.c
        p = self.p
        # Equation below is from Figure 3, Criterion 3 in
        # Riley, Richard D., et al. "Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study." BMJ 384 (2024).
        # Authors say “we recommend values se≤0.0255, so that the confidence interval width is ≤0.1.”
        se = np.sqrt(
        c * (1-c) * (1+
        (N/2-1)*
        (1-c)/(2-c)+
        (N/2-1)*c/(1+c) 
        ) / (N**2 * p * (1-p))   
        )
        return se
    
    def cal_N(self, N_max = int(1e6)):
        my_range = list(range(1, N_max))
        res = np.array(list(map(self.se_cal, my_range)))
        pos = np.abs(res - self.targ_se).argmin()
        return my_range[pos]
    
    def cal_N_loop(self, N_max = int(1e6)):
        err = []
        for i, N in enumerate(range(1, N_max)):
            err.append(np.abs(self.se_cal(N) - self.targ_se))
            if i > 1:
                if err[i] > err[i-1]:
                    return N - 1
        return f"N>{N_max}"    

# Confirm result from the aforementioned paper
# "This calculation gives a minimum required sample size of [...] 347 (149 events) for c statistic,"            
#ins = collins_c(.77, .43, targ_se = .0255)
#ins.cal_N_loop() # output is 347