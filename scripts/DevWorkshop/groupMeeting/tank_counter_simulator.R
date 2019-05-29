# Parameter: Tanks 

sample = c(14,40,105)
M = max(sample)
X = mean(sample)

# Estimator 

# class
t1 = M + X/sqrt(2)
t2 = M + X/2
t3 = M + 2* sd(sample)
t4 = (X + M)/ 2
tm = M + M/length(sample)

t5 = (t1 + t2 + t3 + t4)/4 

# Statistic
c = 140

Ground_Truth <- 140 

set.seed(1)

c <- sample(seq(1:140), 3)
ct = replicate(1000,sample(seq(1:140), 3, replace = FALSE))
sample_test <- t(ct)

xy.list <- split(sample_test, seq(nrow(sample_test)))
theta_function <- function(x){
  # x denotes sample row 
  #sample = c(14,40,105)
  sample = x 
  M = max(sample)
  X = mean(sample)
  
  # Estimator 
  
  # class
  t1 = M + X/sqrt(2)
  t2 = M + X/2
  t3 = M + 2* sd(sample)
  #t3 = M + M/length(x)
  t4 = (X + M)/ 2
  
  t5 = (t1 + t2 + t3 + t4)/4 
  return(cbind(t1,t2,t3,t4,t5))
}



theta_function(c)
theta_columns <- lapply(xy.list, theta_function)

val <- t(bind_rows(theta_columns))
ground_truth <- 140 
samplex <- cbind(ground_truth,sample_test,val)

colnames(samplex) <- c("ground_truth", 
                       "sample1", 
                       "sample2",
                       "sample3",
                       "theta1",
                       "theta2",
                       "theta3",
                       "theta4",
                       "theta5")

DF <- as.data.frame(samplex)

list2 <- lapply(DF, function(x) as.numeric(as.character(x)))
df2 <- as.data.frame(bind_rows(list2))


samplex_results <- df2 %>% 
                      mutate(theta1_mse = (ground_truth - theta1)^2) %>% 
                      mutate(theta2_mse = (ground_truth - theta2)^2) %>% 
                      mutate(theta3_mse = (ground_truth - theta3)^2) %>% 
                      mutate(theta4_mse = (ground_truth - theta4)^2) %>% 
                      mutate(theta5_mse = (ground_truth - theta5)^2) 

mean(samplex_results$theta1)
mean(samplex_results$theta2)
mean(samplex_results$theta3)
mean(samplex_results$theta5)

mean(samplex_results$theta1_mse)
mean(samplex_results$theta2_mse)
mean(samplex_results$theta3_mse)
mean(samplex_results$theta4_mse)
mean(samplex_results$theta5_mse)

sd(samplex_results$theta1_mse)
sd(samplex_results$theta2_mse)
sd(samplex_results$theta3_mse)
sd(samplex_results$theta4_mse)
sd(samplex_results$theta5_mse)

 
                                      
                                      
                                      
