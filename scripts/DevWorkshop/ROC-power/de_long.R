library(pROC)

# load the data_mod.csv file
data_mod <- read.csv("data_mod.csv")

# Calculate ROC curves for the random forest and MLP model
roc_rf <- roc(data_mod$y, data_mod$y_hat_rf)
roc_mlp <- roc(data_mod$y, data_mod$y_hat_mlp)

# To compare the corresponding two (true, unkown) AUCs,
# calculate the p-value from DeLong test
roc.test(roc_rf, roc_mlp, method="delong")$p.value
