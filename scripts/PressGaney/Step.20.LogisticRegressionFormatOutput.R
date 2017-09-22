# Test reporting of logistic regression model results into table and forest plot
# https://cran.r-project.org/web/packages/forestplot/vignettes/forestplot.html
library(forestplot);

# Model that was generated from glm or similar process
model = model.logistic75;

# Report logistic regression model coefficients in exponential form as adjusted odds ratios and 95% confidence intervals
results = list();
results$estimate = exp(model$coefficients);
results$confint = exp(confint.default(model, level=0.95));
results$confint.low = results$confint[,1];
results$confint.high = results$confint[,-1];

write.csv(results, file = "regressionResults.csv", row.names=FALSE, na="")

# Pinch off "infinite" values for extremely wide confidence intervals so can be processed on plot
results$confint.high[results$confint.high == Inf] = 100;

forestplot( 
  labeltext=labels(results$estimate), 
  mean=results$estimate,
  lower=results$confint.low, 
  upper=results$confint.high, 
  clip=c(1/3.0,3.0), # Min and max plot values
  zero=1, # Where to plot zero / base line
);




