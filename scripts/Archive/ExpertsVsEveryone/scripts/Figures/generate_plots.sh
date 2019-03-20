export SCRIPT_DIR=/Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/analysis
export UNMATCHED_EVERYONE=/Users/jwang/Desktop/Results/unmatched/item_associations_everyone_unmatched
export UNMATCHED_EXPERT=/Users/jwang/Desktop/Results/unmatched/item_associations_expert_unmatched

###### ROC Curves ######

# Unmatched, Expert
python $SCRIPT_DIR/ROCPlot.py $UNMATCHED_EXPERT/chest_pain_outcome_input.tab $UNMATCHED_EXPERT/chest_pain_roc_output.tab -f $UNMATCHED_EXPERT/chest_pain_expert_roc.png -n 1000
python $SCRIPT_DIR/ROCPlot.py $UNMATCHED_EXPERT/gi_bleed_outcome_input.tab $UNMATCHED_EXPERT/gi_bleed_roc_output.tab -f $UNMATCHED_EXPERT/gi_bleed_expert_roc.png -n 1000
python $SCRIPT_DIR/ROCPlot.py $UNMATCHED_EXPERT/pneumonia_outcome_input.tab $UNMATCHED_EXPERT/pneumonia_roc_output.tab -f $UNMATCHED_EXPERT/pneumonia_expert_roc.png -n 1000

# Unmatched, Everyone
python $SCRIPT_DIR/ROCPlot.py $UNMATCHED_EVERYONE/chest_pain_outcome_input.tab $UNMATCHED_EVERYONE/chest_pain_roc_output.tab -f $UNMATCHED_EVERYONE/chest_pain_everyone_roc.png -n 1000
python $SCRIPT_DIR/ROCPlot.py $UNMATCHED_EVERYONE/gi_bleed_outcome_input.tab $UNMATCHED_EVERYONE/gi_bleed_roc_output.tab -f $UNMATCHED_EVERYONE/gi_bleed_everyone_roc.png -n 1000
python $SCRIPT_DIR/ROCPlot.py $UNMATCHED_EVERYONE/pneumonia_outcome_input.tab $UNMATCHED_EVERYONE/pneumonia_roc_output.tab -f $UNMATCHED_EVERYONE/pneumonia_everyone_roc.png -n 1000

# Matched, Expert

# Matched, Everyone

###### Precision-Recall Curves ######

# Unmatched, Expert

# Unmatched, Everyone
#python $SCRIPT_DIR/AccuracyPerTopItems.py $UNMATCHED_EVERYONE/chest_pain_outcome_input.tab $UNMATCHED_EVERYONE/chest_pain_pr_output.tab -f $UNMATCHED_EVERYONE/chest_pain_pr.png -m 1500 -x recall:score,precision:score -o outcome

# Matched, Expert

# Matched, Everyone