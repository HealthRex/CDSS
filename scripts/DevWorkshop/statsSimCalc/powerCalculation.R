# Manually prepare a simulated data frame with one patient/observation per row
# A binary treatment indicator (e.g., medication) and a resulting binary outcome (e.g., death within 30 days)
patientId = c(1,2,3,4,5,6,7,8,9,10)
treated   = c(0,0,0,0,0,1,1,1,1,1)
outcome   = c(0,0,0,1,1,0,1,1,1,1)
dfManual = data.frame(patientId, treated, outcome)

# After sourcing this file, try inspecting the contents of the dataframes and doing some basic calculations
# https://www.datacamp.com/community/tutorials/contingency-tables-r
# > source("/<filePath>/powerCalculation.R")    # Specify the full path where you stored and run the contents in your console
# > df = dfManual # Reassign to a simple df (dataframe) working variable name for convenience
# > head(df)  # Look at the top several rows of the dataframe
# > table(df$treated, df$outcome) # Prepare a 2x2 contingency table out of the treated and outcome columns
# > chisq.test(df$treated, df$outcome)  # Calculate Chi-square test to assess for independence between the treated and outcome columns (Note the warning that Chi-square is an approximation that may not be correct for small datasets with cell counts <5)
# > fisher.test(df$treated, df$outcome) # Calculate Fisher exact test to assess for independence between the treated and outcome columns
# Example to illustrate observed vs. expected cell counts if assume independence between treated and outcome
# > result = chisq.test(df$treated, df$outcome)
# > result$observed
# > result$expected



# Define a function to generate simulated data for binary treatment and outcomes
# - nPatients: Number of patient rows to generate
# - nTreated: Number of patient rows to consider treated (rest will be considered untreated)
# - probOutcomeUntreated: Probability that a patient will have the outcome if they were not treated
# - probOutcomeTreated: Probability that a patient will have the outcome if they were treated (these parameters are generally unknown in real life, and is what we're trying to estimate in research)
simulateBinaryTreatmentOutcome = function(nPatients, nTreated, probOutcomeUntreated, probOutcomeTreated)
{
  nUntreated = nPatients - nTreated

  patientId = 1:nPatients # Generate a sequence of ID values from 1,2,3,...,nPatients
  
  treated = c( rep(0,nUntreated), rep(1,nTreated) ) # Generate repeating sequences of 0,0,0,...,0,1,1,1,...1 to reflect which patients received the treatment
  
  untreatedOutcomes = rbinom(nUntreated, 1, probOutcomeUntreated) # Randomly generate binary (binomial of size=1) outcome results for the untreated group
  treatedOutcomes   = rbinom(nTreated,   1, probOutcomeTreated)
  outcome = c( untreatedOutcomes, treatedOutcomes )
  
  dfSim = data.frame(patientId, treated, outcome)
  return(dfSim)
}

# Programmatically generate simulated data for a progressively larger numbers of cases
# Try repeating some of the inspection and test calculations on this dataframe as in the prior manual example
dfSample10  = simulateBinaryTreatmentOutcome(nPatients= 10, nTreated= 5, probOutcomeUntreated=0.4, probOutcomeTreated=0.2)
dfSample40  = simulateBinaryTreatmentOutcome(nPatients= 40, nTreated=20, probOutcomeUntreated=0.4, probOutcomeTreated=0.2)
dfSample100 = simulateBinaryTreatmentOutcome(nPatients=100, nTreated=50, probOutcomeUntreated=0.4, probOutcomeTreated=0.2)



# Define a function to run a batch of simulations (like running the same randomized controlled trial over and over again)
# and collect the Fisher exact test p.values and estimated odds ratio effect estimates across all trials.
# This will then allow us empirically estimate how often (how likely) a simultation/trial will 
# yield a "significant" result with p.value < 0.05 (alpha value) and the range of effect estimates
# - nSims: Number of simulations to run
# - simParams: List of the parameters needed for each simulation (e.g, simParams$nPatients, simParams$nTreated, ...)
batchSimulateBinaryTreatmentOutcome = function(nSims, simParams)
{
  pValues = vector()
  oddsRatios = vector()
  for( i in 1:nSims )
  {
    dfSample = simulateBinaryTreatmentOutcome(simParams$nPatients, simParams$nTreated, simParams$probOutcomeUntreated, simParams$probOutcomeTreated)
    fisherResults = fisher.test(dfSample$treated, dfSample$outcome)
    pValues = append(pValues, fisherResults$p.value) # This is probably an inefficient repeated vector copy
    oddsRatios = append(oddsRatios, fisherResults$estimate)
  }
  batchSimResults = list("pValues"=pValues, "oddsRatios"=oddsRatios)
}


# Type I error rate estimation
# Run a batch of sims to empirically estimate Type I error rate:
# How often a "significant" difference is detected when there is none (i.e., probOutcomeUntreated = probOutcomeTreated))
# In theory, the type1ErroRate should equal the pre-specified alpha, since that is the definition
nSims = 1000
simParams = list("nPatients"=40, "nTreated"=20, "probOutcomeUntreated"=0.4, "probOutcomeTreated"=0.4)
alpha = 0.05  # P-value threshold at which to consider a difference to be "statistically significant" or not
batchSimResults = batchSimulateBinaryTreatmentOutcome(nSims, simParams)
type1Errors = (batchSimResults$pValues < alpha) # Since we know there is no (only random) difference between treated and untreated outcome rates, it is a type 1 error if the p-value isless than the alpha significance threshold. Track how often this happens
type1ErrorRate = mean(type1Errors) # By interpreting the individual errors as binary (0,1) values, the mean value can be interpreted as a percentage rate


# Type II error rate estimation
# Run a batch of sims for an example set of parameters to empirically estimate Type II error rate (how often "no difference" is detected when there is one)
nSims = 1000
simParams = list("nPatients"=40, "nTreated"=20, "probOutcomeUntreated"=0.4, "probOutcomeTreated"=0.2)
alpha = 0.05  # P-value threshold at which to consider a difference to be "statistically significant" or not
batchSimResults = batchSimulateBinaryTreatmentOutcome(nSims, simParams)
type2Errors = (batchSimResults$pValues >= alpha) # Since we know there is a difference between treated and untreated outcome rates, it is a type 2 error if the p-value is not less than the alpha significance threshold. Track how often this happens
type2ErrorRate = mean(type2Errors) # By interpreting the individual errors as binary (0,1) values, the mean value can be interpreted as a percentage rate






#Binary Outcome
#(Similar to above, but binomial distributions)
#1 - Generate samples from binomial distributions with pre-specified rates
#2 - Given two samples of binary outcomes, calculate p-value for different rate / odds ratio (e.g., Chi-square or Fisher Exact)
#3 - Visualize ratio bar charts with estimated rates for actual and samples
#4 - Simulate 1,000 runs of above to estimate Type I and Type II error rates
#5 - Animate how changes in distributions (different rates, different sample sizes) will yield different expected Type I and Type II error rates.
#
#
# Plot p-value + confidence interval as function of increasing sample size, of average treatment effect, of class imbalance
#
#
#
#Predicted Confidence Intervals
#
#
#
#Bootstrapping Confidence Intervals
#- Mean estimate +/- 1.96 std errors
#- PPV estimate (mean estimate)
#- AUROC confidence interval
#
#
#Dataset size necessary for prediction models / feature/covariate count???
