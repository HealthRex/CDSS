= Dev Workshop =
Power Calculations - Empirically Estimating by Simulation

== Learning Goals ==
- Basic R DataFrame manipulation, including dplyr
- Basic Categorical Hypothesis Testing with Chi-square and Fisher exact test
- Meaning and relationships between Type I Error, Type II Error, alpha, beta, confidence intervals, p-values
- Relationship of Statistical Power with sample size, sample imbalance, treatment effect


== Preconditions ==
- R and R Studio installed
  - install.packages("dplyr","reshape2")
- Git installed so able to download / clone code repository
- Suggest online pre-reading to review Power calculations, Type I error, Type II error, alpha, beta, etc.

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

  When you see an extended comment header ############ like
  ########## For the manually constructed treatment vs. outcome data above, what is p-value for for whether the treatment affects the outcome?
  This means to pause and review the conceptual question

- Beware that the above largely applies to prospective experiments / data collection / study design planning.
  Once data is already collected, retrospective analysis / building predictive models, etc., a "post-hoc power analysis" generally doesn't make sense.
  Similar but alternative approaches are necessary to estimate whether a given database sample size is likely sufficient to conduct such a study.


== Further Reading ==
The Use of Predicted Confidence Intervals When Planning Experiments and the Misuse of Power When Interpreting Results
Steven N. Goodman, MD, PhD, Jesse A. Berlin, ScD
https://www.acpjournals.org/doi/10.7326/0003-4819-121-3-199408010-00008

