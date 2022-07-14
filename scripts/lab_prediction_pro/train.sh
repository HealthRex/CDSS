# tasks=(label_WBC label_PLT label_HGB)

# for task in ${tasks[@]}
# do
# python driver.py --run_name 20220705_cbc \
#     --trainer BoostingTrainer \
#     --tasks $task
# done

# tasks=(label_WBC label_PLT label_HGB)

# tasks=(label_NA label_K label_CO2 label_BUN label_CR label_CA label_ALB)
# for task in ${tasks[@]}
# do
# python driver.py --run_name 20220705_metabolic_comp \
#     --trainer BoostingTrainer \
#     --tasks $task
# done


# Magnesium
# python driver.py --run_name 20220705_magnesium \
#     --cohort MagnesiumCohort \
#     --featurizer BagOfWordsFeaturizerLight \
#     --trainer BoostingTrainer \
#     --tasks label_MG \
#     --tfidf

# Blood cultures
# python driver.py --run_name 20220705_blood \
#     --cohort BloodCultureCohort \
#     --featurizer BagOfWordsFeaturizerLight \
#     --trainer BoostingTrainer \
#     --tasks label_blood \
#     --tfidf

# Urine cultures
python driver.py --run_name 20220705_urine \
    --cohort UrineCultureCohort \
    --featurizer BagOfWordsFeaturizerLight \
    --trainer BoostingTrainer \
    --tasks label_urine \
    --tfidf


