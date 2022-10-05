library(pROC) # Library to facilitate standard roc calculations

# Examples to illustrate calculating 
# - Area under ROC (receiver operating characteristic) curve
# - Bootstrap confidence intervals

# A nice review blog post
# https://glassboxmedicine.com/2020/02/04/comparing-aucs-of-machine-learning-models-with-delongs-test/

# Manually prepare a simulated data frame with one case/observation per row
# A continuous numerical indicator (e.g., prediction score, lab value, age, etc.) 
#   and a respective binary outcome label (e.g., diagnosis or death within 30 days)
caseId  = c(1,2,3,4,5,6,7,8,9,10)
score = c(0.2, 0.3, 0.35, 0.5, 0.5, 0.7, 0.75, 0.8, 0.85, 0.9)
label = c(  0,   0,    0,   1,   1,   0,    1,   1,    1,   1)
dfManualScore = data.frame(caseId, score, label)

# Use an existing package for ROC analysis
rocManualScore = roc(label, score)
# > rocManualScore$auc  # Check calculated AUROC value

########## How well do you think a model that produced the above results would do in general for new cases?
########## How confident are you that the good results weren't just a fluke with the small sample size?

# Define a function to generate simulated data for binary label classification scoring
# - nCases: Number of case rows to generate
# - nPositive: Number of case rows with a positive label (rest will be negative). nPositive/nCases reflects the prevalence in the sample.
# - negMean: Mean score generated from negative cases
# - posMean: Mean score generated from positive cases
# - negStdDev: Standard deviation for score generated from negative cases
# - posStdDev: Standard deviation for score generated from positive cases
simulateBinaryClassificationScores = function(nCases, nPositive, negMean, negStdDev, posMean, posStdDev)
{
  nNegative = nCases - nPositive
  
  caseId = 1:nCases # Generate a sequence of ID values from 1,2,3,...,nCases
  
  label = c( rep(0,nNegative), rep(1,nPositive) ) # Generate repeating sequences of 0,0,0,...,0,1,1,1,...1 to reflect which patients have the target label
  
  negativeScores = rnorm(nNegative, negMean, negStdDev) # Randomly generate normally distributed scores for the negative group
  positiveScores = rnorm(nPositive, posMean, posStdDev) # Randomly generate normally distributed scores for the negative group
  
  score = c( negativeScores, positiveScores )
  
  dfSim = data.frame(caseId, score, label)
  return(dfSim)
}


# Simulate two distributions, one for positive cases and one for negative ones,
#   (usually you don't actually know which ones are actually positive or negative, 
#   that's what you're trying to predict/guess/classify)
# Each with a normal distribution of producing different score values
# For example those who have a heart attack vs. those who don't,
#   expect the average cholesterol level (score) to have a higher
#   average in the positive group, but there will be a range of
#   (overlapping) values in both, reflected by the standard deviation
#   of the two distributions.
dfSampleScore10 = simulateBinaryClassificationScores(nCases=10, nPositive=3, negMean=100, negStdDev=40, posMean=150, posStdDev=20)
dfSampleScore100 = simulateBinaryClassificationScores(nCases=100, nPositive=30, negMean=100, negStdDev=40, posMean=150, posStdDev=20)
dfSampleScore1000 = simulateBinaryClassificationScores(nCases=1000, nPositive=300, negMean=100, negStdDev=40, posMean=150, posStdDev=20)

# Convenience function for plotting a histogram of the values in two labeled distributions (expected to equal 0 and 1)
quickPlotHistogram = function( values, labels )
{
  hist(values[labels==0], col=rgb(0,0,1,0.5), breaks=20, xlim=c(0,max(values))) # Blue RGB color with 1/2 transparency
  hist(values[labels==1], col=rgb(1,0,0,0.5), breaks=20, add=TRUE) # Add to existing plot, 20 bins. 
  # Assumes 0 is more common label, so will get y-limit default right the first time
}

# Plot a histogram showing the overlapping distributions of positive and negative cases
# Note the "Bayes error rate" reflected in where the distributions overlap, making it impossible to get perfect classification/discrimination
# > quickPlotHistogram( dfSampleScore1000$score, dfSampleScore1000$label )

# Plot the ROC curve for how well the score separates the two classes
# > rocResult = roc(dfSampleScore1000$label, dfSampleScore1000$score, ci=TRUE)
# > plot(rocResult, print.auc=T)


