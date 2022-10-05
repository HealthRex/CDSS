= Dev Workshop =
Power Calculations - Empirically Estimating by Simulation

== Learning Goals ==
- Basic R DataFrame manipulation, including dplyr
- Basic Categorical Hypothesis Testing with Chi-square and Fisher exact test
- Meaning and relationships between Type I Error, Type II Error, alpha, beta, confidence intervals, p-values
- Relationship of Statistical Power with sample size, sample imbalance, treatment effect


== Preconditions ==
- R installed
  - install.packages("dplyr","reshape2")
  - Convenient to also install RStudio and bonus points for getting R to work in Jupyter notebooks (https://www.datacamp.com/community/blog/jupyter-notebook-r)
- Git installed so able to download / clone code repository
- Suggest online pre-reading to review Power calculations, Type I error, Type II error, alpha, beta, etc.


== Example Questions you Should be Able to Answer ==
- If patients with a disease die within 1 year 35% of the time and you believe treating them with your new device will reduce the death rate to 20%, how many patients would you need to recruit for a clinical trial if we want a 90% chance of detecting/showing the benefit of treatment when considering 0.05 to be a "significant" p-value?

- If you only have enough budget to recruit 50 patients, what are the chances you will get a positive study (i.e., you detect the difference above with p-value <0.05)? What will you conclude if you end up with a negative study (i.e., p>0.05)?

- You believe your fancy machine learning model can better predict and diagnose diseases than doctors, as doctors are only 70% accurate when predicting a patient outcome (e.g., death, hospitalization, readmission, etc.). You have access to a database of 500 prior cases, for which you plan to hold out 20% as a test set. How accurate would your model have to be to have a better than 90% chance of showing it to be "statistically significantly" better than the baseline 70%?


== Workshop Steps ==
- Download copy of the code repository
    git clone https://github.com/HealthRex/CDSS.git
       or if you just need to update existing copy...
    git pull

- Open the following scripts in CDSS/scripts/DevWorkshop/statsSimCalc directory in RStudio
  powerCalculation.R
  powerCalculation.examples.R 

- "source" each of the above two files to load/execute them (the latter will take a minute as it runs through a battery of simulations)

- Step through the code in the above example files 
  
  If you don't understand what's happening in any lines of code, then ask for input

  When you see comment lines that start with "# >" like
  # > head(dfManual)
  This means you can try to copy-paste the command after the > and execute it in the interactive console.

  When you see an extended comment header ############ Question text...
  This means to pause and review the conceptual question

- Beware that the above largely applies to prospective experiments / data collection / study design planning.
  Once data is already collected, retrospective analysis / building predictive models, etc., a "post-hoc power analysis" generally doesn't make sense.
  Similar but alternative approaches are necessary to estimate whether a given database sample size is likely sufficient to conduct such a study.


== Further Reading ==
The Use of Predicted Confidence Intervals When Planning Experiments and the Misuse of Power When Interpreting Results
Steven N. Goodman, MD, PhD, Jesse A. Berlin, ScD
https://www.acpjournals.org/doi/10.7326/0003-4819-121-3-199408010-00008


Casting New Light on Statistical Power: An Illuminating Analogy and Strategies to Avoid Underpowered Trials
Michaela Kiernan, Michael T Baiocchi
https://academic.oup.com/aje/article-abstract/191/8/1500/6549167

https://clincalc.com/stats/SampleSize.aspx


