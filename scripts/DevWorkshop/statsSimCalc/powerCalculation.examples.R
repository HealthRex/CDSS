# Depends on powerCalculation.R to be sourced first

# Example simulate results where probOutcomeUntreated == probOutcomeTreated 
#   (i.e., null hypothesis is true, where outcome rates are independent of any treatment effect) 
nullResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( nPatients=c(32,64,128,256,512,1024), nTreatedRange=c(0.50), probOutcomeUntreatedRange=c(0.4), probOutcomeTreatedRange=c(0.4), nSimsPerCombo=1000, alpha=0.05 )
#
########## How likely do you expect to reject the null hypothesis with increasing sample size if you know there is no treatment effect here?
########## Explain what the "%>% select" command does to the dataframe contents
# Plot the x-axis (nPatients) and the empiric null hypothesis reject rate. In theory, this should always = alpha, since that's the definition
# > quickPlotDF( nullResultDF %>% select(nPatients, nullHypothesisRejectRate), "Type I Error Rate = alpha","bottomright")  # Since we know the null hypothesis is true here, the rejection rate is the Type I error rate
#
########## What do you expect the median and shape of the 95% confidence intervals to be for the estimated odds ratio with increasing sample size?
# Plot the x-axis (nPatients) and the oddsRatio estimates and confidence interval ranges to see how they change with respect to data size
# > quickPlotDF( nullResultDF %>% select(nPatients, oddsRatioCILow, oddsRatioMean, oddsRatioMedian, oddsRatioCIHigh), "Odds Ratio Estimates")
#
#
# Review cases where probOutcomeUntreated != probOutcomeTreated 
#   (i.e., null hypothesis is false. There is a treatment effect on the outcome) 
nonNullResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( nPatients=c(32,64,128,256,512,1024), nTreatedRange=c(0.50), probOutcomeUntreatedRange=c(0.2), probOutcomeTreatedRange=c(0.4), nSimsPerCombo=1000, alpha=0.05 )
#
########## How can we estimate the statistical power of these simulated studies and how do you expect that to change with increasing sample size?
# Plot the x-axis (nPatients) and the empiric null hypothesis non-reject rate (i.e., Power). 
# > quickPlotDF( nonNullResultDF %>% select(nPatients, nullHypothesisRejectRate), "Power = 1-Beta","bottomright")  # Since we know the null hypothesis is false here, the reject rate is the Power = 1 - Beta (Type II error rate)
#
########## How do you expect the shape of the 95% confidence intervals to be for the estimated odds ratio with increasing sample size when there is a known treatment effect?
# Plot the x-axis (nPatients) and the oddsRatio estimates and confidence interval ranges to see how they change with respect to data size
# > quickPlotDF( nonNullResultDF %>% select(nPatients, oddsRatioCILow, oddsRatioMean, oddsRatioMedian, oddsRatioCIHigh), "Odds Ratio Estimates")


# Example simulations with increasing total sample sizes, but same (small) number of treated cases. Illustrate that power depends on your smaller class size, not the total sample size
imbalancedResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( nPatients=c(32,64,128,256,512,1024), nTreatedRange=c(16), probOutcomeUntreatedRange=c(0.2), probOutcomeTreatedRange=c(0.4), nSimsPerCombo=1000, alpha=0.05 )
########## Review the two dataframes being "joined" here and explain what the inner_join does
# Join the imbalanced results with the 50:50 balanced results to compare the progression of Power with sample size
balancedVsImbalancedDF = inner_join( nonNullResultDF[c("nPatients","nullHypothesisRejectRate")], imbalancedResultDF[c("nPatients","nullHypothesisRejectRate")], by=c("nPatients") )
colnames(balancedVsImbalancedDF) = c("nPatients","nTreated = 50%","nTreated = 16")  # Rename columns to clarify comparison
#
########## Are you better off studying 1000 total patients, 20 of which are treated, or 200 total patients, 100 of which are treated?
# > quickPlotDF(balancedVsImbalancedDF, "Power = 1-Beta","bottomright")


# Example simulations with increasing average treatment effect (larger difference between outcome probabilities). Illustrate that power depends on how small an effect is to be detected (and very hard to detect small differences)
treatmentEffectResultDF = batchSimulateBinaryTreatmentOutcomeAcrossParameters( nPatients=c(32,64,128,256,512,1024), nTreatedRange=c(0.50), probOutcomeUntreatedRange=c(0.3,0.4,0.45,0.48,0.50), probOutcomeTreatedRange=c(0.5,0.5,0.5,0.5,0.5), nSimsPerCombo=1000, alpha=0.05 )
treatmentEffectResultDF$averageTreatmentEffectLabel = paste("ATE",format(treatmentEffectResultDF$averageTreatmentEffect))
########## Review the "long" vs. "wide" dataframes and explain what the "pivot table" dcast does to the structure of the data (see also https://tidyr.tidyverse.org/articles/pivot.html)
# PivotTable to reshape-dcast long-format data into wide-format, so can compare effect of multiple parameters simultaneously: https://www.r-bloggers.com/pivot-tables-in-r/
longTreatmentEffectResultDF = treatmentEffectResultDF %>% select(nPatients,averageTreatmentEffectLabel,nullHypothesisRejectRate)
wideTreatmentEffectResultDF = dcast(longTreatmentEffectResultDF, nPatients ~ averageTreatmentEffectLabel)
########## If you needed 100,000 patients to reliably detect a treatment effect, does the treatment even matter?
# > quickPlotDF(wideTreatmentEffectResultDF,"Power","topleft")

