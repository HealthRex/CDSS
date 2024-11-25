import pandas as pd

# read from the layest pickle file
llm_prefill = pd.read_pickle('../pickle/llm_prefill_20241120_214031.pkl')

# Assuming llm_prefill is your dataframe
import numpy as np

max_len = llm_prefill.applymap(lambda x: len(x)).max().max()
frac_less_than_x = np.array([llm_prefill.applymap(lambda x: len(x)<i).mean().mean() for i in range(max_len+1)])
# plot frac_less_than_x with xlim=(0, 1000)
import matplotlib.pyplot as plt
plt.plot(frac_less_than_x)
plt.xlim(0, 1000)
plt.xlabel('Length of string')
plt.ylabel('Fraction of strings')
plt.title('Fraction of strings with length less than x')
plt.show()

# Set the maximum length to 250 for all strings
llm_prefill = llm_prefill.applymap(lambda x: x[:250])

to_extract = ["reason for admission",
                "relevant medical and surgical history",
                "primary and secondary diagnoses",
                "key investigations and results",
                "procedures performed",
                "social context",
                "plan for follow up",
                "medications changed during admission and the indications for this",
                "medications to be reviewed by the primary care physician and why",
                "actions the primary care physician should take post discharge"]

for i,v in enumerate([i.capitalize() for i in to_extract]):
    pos = 4 * i
    llm_prefill.insert(pos, f'axis_{i+1}', v)
    
llm_prefill.to_csv('../exports/formated_llm_prefill.csv', index=False)