library(epiR)
dat <- as.table(matrix(c(.99,50,0.01,949), nrow = 2, byrow = TRUE))
colnames(dat) <- c("Dis+","Dis-")
rownames(dat) <- c("Test+","Test-")
rval <- epi.tests(dat, conf.level = 0.95)
print(rval); summary(rval)

## Test sensitivity is 0.90 (95% CI 0.88 -- 0.92). Test specificity is 
## 0.76 (95% CI 0.73 -- 0.79). The likelihood ratio of a positive test 
## is 3.75 (95% CI 3.32 to 4.24). The number needed to diagnose is 
## 1.51 (95% CI 1.41 to 1.65). Around 15 persons need to be tested 
## to return 10 positive tests.
# }
