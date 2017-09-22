# Load source table to data frame

setwd("C:/GoogleDrive/OpioidRx/PressGaney/");
dataFile = "PressGaney-MedicareOpioid.Stanford2014.tab";
#dataFile = "sample.tab";
rawDF = read.table(dataFile, header = T, sep = "\t", na.strings = "None", quote="\"");
df = rawDF;


# Only look at doctors with at least 5 surveys and more than 5 opioid claims
df.min5data = df[df$survey_n >= 5 & df$opioid_claim_count_c05 >5,];

# Calculate percentiles for hitting percent likelihood to recommend in "top box" (i.e., 5 out of 5)
ltr_top_box_50percentile = quantile(df.min5data$survey_percent_ltr_top_box, 0.50);
ltr_top_box_75percentile = quantile(df.min5data$survey_percent_ltr_top_box, 0.75);
ltr_top_box_85percentile = quantile(df.min5data$survey_percent_ltr_top_box, 0.85);
ltr_top_box_90percentile = quantile(df.min5data$survey_percent_ltr_top_box, 0.90);

df.min5data$ltr_top_box_over50percentile = df.min5data$survey_percent_ltr_top_box > ltr_top_box_50percentile;
df.min5data$ltr_top_box_over75percentile = df.min5data$survey_percent_ltr_top_box > ltr_top_box_75percentile;
df.min5data$ltr_top_box_over85percentile = df.min5data$survey_percent_ltr_top_box > ltr_top_box_85percentile;
df.min5data$ltr_top_box_over90percentile = df.min5data$survey_percent_ltr_top_box > ltr_top_box_90percentile;

# Reorder specialty ordering so Internal Medicine (most common specialty) is referenced as baseline
referenceSpecialtyIndex = match("Internal Medicine", levels(df.min5data$specialty_description));
df.min5data$specialty = relevel(df.min5data$specialty_description, ref=referenceSpecialtyIndex);


# Logistic regression formula outcome and dependencies (independent variables)
formula.logistic50 = ltr_top_box_over50percentile ~ gender + survey_n + specialty + total_claim_count + opioid_prescriber_rate;
#formula.logistic = ltr_top_box_over50percentile ~ opioid_prescriber_rate;
#formula.logistic = ltr_top_box_over50percentile ~ opioid_claim_count;
model.logistic50 = glm(formula.logistic50, family=binomial(link="logit"), data=df.min5data);

# Logistic regression for hitting 75th LTR top box percentile
formula.logistic75 = ltr_top_box_over75percentile ~ gender + survey_n + specialty + total_claim_count + opioid_prescriber_rate;
#formula.logistic = ltr_top_box_over50percentile ~ opioid_prescriber_rate;
#formula.logistic = ltr_top_box_over50percentile ~ opioid_claim_count;
model.logistic75 = glm(formula.logistic75, family=binomial(link="logit"), data=df.min5data);

# Direct linear regression on % likelihood to recommend top box
formula.ltrTopBox = survey_percent_ltr_top_box ~ gender + specialty + survey_n + total_claim_count + opioid_prescriber_rate;
#formula.ltrTopBox = survey_percent_ltr_top_box ~ opioid_prescriber_rate;
#formula.ltrTopBox = survey_percent_ltr_top_box ~ opioid_claim_count;
model.ltrTopBox = glm(formula.ltrTopBox, data=df.min5data);

# Direct linear regression on avereage likelihood to recommend score
formula.ltrAvg = survey_avg ~ gender + specialty + survey_n + total_claim_count + opioid_prescriber_rate;
#formula.ltrAvg = survey_avg ~ opioid_prescriber_rate;
#formula.ltrAvg = survey_avg ~ opioid_claim_count;
model.ltrAvg = glm(formula.ltrAvg, data=df.min5data);



# Redo with hierarchical model (e.g., GEE or LME) to separate comparisons per Specialty?

