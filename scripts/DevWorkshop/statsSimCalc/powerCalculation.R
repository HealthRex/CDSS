library(dplyr)  # Will use dplyr package for convenient data table manipulation. If not already, then run: install.packages("dplyr")
library(reshape2) # Helps for reshaping Pivot Table data. Likely already included as a dplyr dependency. Otherwise: install.packages("reshape2")

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
# This will then allow us to empirically estimate how often (how likely) a simultation/trial will 
# yield a "significant" result with p.value < 0.05 (alpha value) and the range of effect estimates (odds ratio)
# - nSims: Number of simulations to run
# - simParams: List of the parameters needed for each simulation (e.g, simParams$nPatients, simParams$nTreated, ...)
#
#   Beware that if you simulate a small number of patients and small probability of outcomes, it's possible
#   that some simulations will result in nobody in a group having the outcome at all, at which point
#   the pValue and oddsRatio calculations will fail since they don't make sense (divide by zero), yielding the cryptic error message:
#     Error in fisher.test(dfSample$treated, dfSample$outcome) : 
#     'x' and 'y' must have at least 2 levels 
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


# Type I error rate (alpha) estimation
# Run a batch of sims to empirically estimate Type I error rate:
# How often a "significant" difference is detected when there is none (i.e., probOutcomeUntreated = probOutcomeTreated))
# In theory, the type1ErroRate should equal the pre-specified alpha, since that is the definition
nSims = 100
simParams = list("nPatients"=40, "nTreated"=20, "probOutcomeUntreated"=0.4, "probOutcomeTreated"=0.4)
alpha = 0.05  # P-value threshold at which to consider a difference to be "statistically significant" or not
batchSimResults = batchSimulateBinaryTreatmentOutcome(nSims, simParams)
type1Errors = (batchSimResults$pValues < alpha) # Since we know there is no (only random) difference between treated and untreated outcome rates, it is a type 1 error if the p-value is less than the alpha significance threshold. Track how often this happens
type1ErrorRate = mean(type1Errors) # By interpreting the individual errors as binary (0,1) values, the mean value can be interpreted as a percentage rate
nullOddsRatio95CI = quantile( batchSimResults$oddsRatios, c(0.025,0.975) ) # Empirically estimated 95% confidence interval for odds ratio. In null hypothesis case, the true odds ratio should = 1

# Type II error rate (beta) estimation
# Run a batch of sims for an example set of parameters to empirically estimate Type II error rate (how often "no difference" is concluded when there actually is one)
nSims = 100
simParams = list("nPatients"=40, "nTreated"=20, "probOutcomeUntreated"=0.4, "probOutcomeTreated"=0.2)
alpha = 0.05  # P-value threshold at which to consider a difference to be "statistically significant" or not
batchSimResults = batchSimulateBinaryTreatmentOutcome(nSims, simParams)
type2Errors = (batchSimResults$pValues >= alpha) # Since we know there is a difference between treated and untreated outcome rates, it is a type 2 error if the p-value is not less than the alpha significance threshold. Track how often this happens
type2ErrorRate = mean(type2Errors) # By interpreting the individual errors as binary (0,1) values, the mean value can be interpreted as a percentage rate
nonNullOddsRatio95CI = quantile( batchSimResults$oddsRatios, c(0.025,0.975) ) # Empirically estimated 95% confidence interval for odds ratio

# Try inspecting the values of the above error rates and confidence intervals




# Define a function to iterate through combinations of simulation parameters to 
# batch simulate scenarios and collect the empirically estimated pValues significance rates and oddsRatio confidence intervals.
# Return the collected results in a long-format data frame with one column per modifiable parameter and one column per result value
# - nPatientsRange: Increasing values of nPatients in the sample size
# - nTreatedRange: How many of the total nPatients in a simulation will be assigned to treatment. If a decimal value < 1.0, then interpret as a percentage of the total nPatients
# - probOutcomeUntreatedRange: Range of untreated outcome rates to simulate
# - probOutcomeTreatedRange: Range of treated outcome rates to simulate (must be same length as probOutcomeUntreatedRange to match)
# - nSimsPerCombo: The number of simulations for each parameter combination
# - alpha: Threshold below which to consider a p-value as "statistically significant" to reject the null hypothesis. Classically use 0.05, corresponding to 95% confidence intervals.
batchSimulateBinaryTreatmentOutcomeAcrossParameters = function(nPatientsRange, nTreatedRange, probOutcomeUntreatedRange, probOutcomeTreatedRange, nSimsPerCombo, alpha)
{
  # Start with data frame, with just column assignments first for parameters and result values of interest
  resultDF = 
    data.frame("nPatients"=numeric(0), "percentTreated"=numeric(0), "probOutcomUntreated"=numeric(0), "probOutcomeTreated"=numeric(0), "averageTreatmentEffect"=numeric(0),
               "nullHypothesisRejectRate"=numeric(0), "nullHypothesisNonRejectRate"=numeric(0), "oddsRatioMean"=numeric(0), "oddsRatioMedian"=numeric(0), "oddsRatioCILow"=numeric(0), "oddsRatioCIHigh"=numeric(0))

  # Iterate through each combination of simulation parameters
  for (nPatients in nPatientsRange)
  {
    for (nTreated in nTreatedRange)
    {
      if ( 0.0 < nTreated & nTreated < 1.0 )
      { # Interpret as a percentage of the total nPatients
        percentTreated = nTreated
        nTreated = as.integer(nPatients * percentTreated) # Overwrite with integer count value
      }

      for (iProbOutcome in 1:length(probOutcomeUntreatedRange)) # Use numeric index to simultaneously iterate through both treated and untreated parameters
      {
        probOutcomeUntreated = probOutcomeUntreatedRange[iProbOutcome]
        probOutcomeTreated = probOutcomeTreatedRange[iProbOutcome]
        
        # Now run a batch of simulations for the given combination of parameters
        simParams = list("nPatients"=nPatients, "nTreated"=nTreated, "probOutcomeUntreated"=probOutcomeUntreated, "probOutcomeTreated"=probOutcomeTreated)
        message(paste(as.character(simParams), collapse=", "))  # Print message before simulation as a progress indicator
        batchSimResults = batchSimulateBinaryTreatmentOutcome(nSimsPerCombo, simParams)
        
        simParams["averageTreatmentEffect"] = probOutcomeTreated - probOutcomeUntreated
        simParams["nullHypothesisRejectRate"] = mean(batchSimResults$pValues < alpha) # Classical frequentist statistics, if p-value is less than the alpha threshold, then reject null hypothesis = "statistically significany differnece detected." Track how often this happens
        simParams["nullHypothesisNonRejectRate"] = 1.0-mean(batchSimResults$pValues < alpha)
        simParams["oddsRatioMean"] = mean(batchSimResults$oddsRatios)
        simParams["oddsRatioMedian"] = median(batchSimResults$oddsRatios)
        simParams["oddsRatioCILow"] = quantile( batchSimResults$oddsRatios, alpha/2 ) # At alpha = 0.05, bottom end of 95% confidence interval corresponds to the 2.5%ile
        simParams["oddsRatioCIHigh"] = quantile( batchSimResults$oddsRatios, 1.0 - alpha/2 )
        
        # Append the parameter and result values to the result data frame
        resultDF = rbind(resultDF, simParams)
      }
    }
  }
  return(resultDF)
}

# Define function to make a quick plot of the first column of the dataframe as the x-axis vs all others as y-axis lines
# - plotDF: Dataframe with data to plot. First column expected to be the x-axis values
# - ylab: Y-axis / value label
# - legendLoc: Where to place the legend. Defaults to top-right of the figure
quickPlotDF = function(plotDF, ylab, legendLoc="topright")
{
  yDF = plotDF[-1] # Remove the "x-axis" column to leave just the "y-axis" value columns
  matplot(plotDF[1], yDF, type=c("b"), pch="+", xlab=colnames(plotDF)[1], ylab=ylab)  # Multi-line plot
  legend(legendLoc, legend=colnames(yDF), col=1:ncol(yDF), lty=1:ncol(yDF))  # Add a legend to the plot that matches the color scheme of the plot
}
  






# Example simulate results where probOutcomeUntreated == probOutcomeTreated 
#   (i.e., null hypothesis is true, where outcome rates are independent of any treatment effect) 
nullResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( c(32,64,128,256,512,1024), c(0.50), c(0.4), c(0.4), 1000, 0.05 )
#
# Plot the x-axis (nPatients) and the empiric null hypothesis reject rate. In theory, this should always = alpha, since that's the definition
# > quickPlotDF( nullResultDF %>% select(nPatients, nullHypothesisRejectRate), "Type I Error Rate = alpha","bottomright")  # Since we know the null hypothesis is true here, the rejection rate is the Type I error rate
#
# Plot the x-axis (nPatients) and the oddsRatio estimates and confidence interval ranges to see how they change with respect to data size
# > quickPlotDF( nullResultDF %>% select(nPatients, oddsRatioCILow, oddsRatioMean, oddsRatioMedian, oddsRatioCIHigh), "Odds Ratio Estimates")
#
#
# Review cases where probOutcomeUntreated != probOutcomeTreated 
#   (i.e., null hypothesis is false. There is a treatment effect on the outcome) 
nonNullResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( c(32,64,128,256,512,1024), c(0.50), c(0.2), c(0.4), 1000, 0.05 )
#
# Plot the x-axis (nPatients) and the empiric null hypothesis non-reject rate (i.e., Power). 
# > quickPlotDF( nonNullResultDF %>% select(nPatients, nullHypothesisRejectRate), "Power = 1-Beta","bottomright")  # Since we know the null hypothesis is false here, the reject rate is the Power = 1 - Beta (Type II error rate)
#
# Plot the x-axis (nPatients) and the oddsRatio estimates and confidence interval ranges to see how they change with respect to data size
# > quickPlotDF( nonNullResultDF %>% select(nPatients, oddsRatioCILow, oddsRatioMean, oddsRatioMedian, oddsRatioCIHigh), "Odds Ratio Estimates")


# Example simulations with increasing total sample sizes, but same (small) number of treated cases. Illustrate that power depends on your smaller class size, not the total sample size
imbalancedResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( c(32,64,128,256,512,1024), c(16), c(0.2), c(0.4), 1000, 0.05 )
#
# Plot the x-axis (nPatients) and the empiric null hypothesis non-reject rate (i.e., Power). 
# > quickPlotDF( imbalancedResultDF %>% select(nPatients, nullHypothesisRejectRate), "Power = 1-Beta","bottomright")  # Since we know the null hypothesis is false here, the reject rate is the Power = 1 - Beta (Type II error rate)
#
# Join the imbalanced results with the 50:50 balanced results to compare the progression of Power with sample size
balancedVsImbalancedDF = inner_join( nonNullResultDF[c("nPatients","nullHypothesisRejectRate")], imbalancedResultDF[c("nPatients","nullHypothesisRejectRate")], by=c("nPatients") )
colnames(balancedVsImbalancedDF) = c("nPatients","nTreated = 50%","nTreated = 16")  # Rename columns to clarify comparison
# > quickPlotDF(balancedVsImbalancedDF, "Power","bottomright")


# Example simulations with increasing average treatment effect (larger difference between outcome probabilities). Illustrate that power depends on how small a sample size is to be detected (and very hard to detect small differences)
treatmentEffectResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( c(32,64,128,256,512,1024), c(0.50), c(0.3,0.4,0.45,0.48,0.50), c(0.5,0.5,0.5,0.5,0.5), 1000, 0.05 )
# PivotTable to reshape-dcast long-format data into wide-format, so can compare effect of multiple parameters simultaneously: https://www.r-bloggers.com/pivot-tables-in-r/
treatmentEffectResultDF$averageTreatmentEffectLabel = paste("ATE",format(treatmentEffectResultDF$averageTreatmentEffect))
wideTreatmentEffectResultDF = dcast(treatmentEffectResultDF %>% select(nPatients,averageTreatmentEffectLabel,nullHypothesisRejectRate), nPatients ~ averageTreatmentEffectLabel)
# > quickPlotDF(wideTreatmentEffectResultDF,"Power","topleft")

