import pdb
import argparse
import sys
import os
import utils.viz_functions as vis_tools


sys.path.append(os.getcwd())
parser = argparse.ArgumentParser()

parser.add_argument("--viz_method", type=str, default="none", choices = ["pca", "tsne", "none"])    
parser.add_argument("--features_to_show", type=str, default="meds_diags_procs", choices = ["meds_diags_procs","all"])    
parser.add_argument("--sampled", type=int, default=1, choices = [0,1])    
parser.add_argument("--sample_size", type=int, default=2000)    
parser.add_argument("--perplex", type=int, default=35)    
parser.add_argument("--num_it", type=int, default=1000)    
parser.add_argument("--lr_rate", type=int, default=200)   

parser.add_argument("--plot_shap", type=int, default=0, choices = [0, 1])    
parser.add_argument("--plot_surv", type=int, default=0, choices = [0, 1])    
parser.add_argument("--descs", type=int, default=0, choices = [0, 1])    
parser.add_argument("--sample_size_for_shap", type=float, default=0.05)  
parser.add_argument("--trained_model_path", type=str, default="saved_classical_ml_models/xgb_model_notenlp_flag1.pkl")    


parser.add_argument("--compute_table_1", type=int, default=0, choices = [0, 1])    
parser.add_argument("--compute_p", type=int, default=0, choices = [0, 1])    
parser.add_argument("--compute_table_progress_report", type=int, default=0, choices = [0, 1])    
parser.add_argument("--plot_violins_flag", type=int, default=0, choices = [0, 1])    


parser.add_argument("--train_stationary_filename", type=str, default="stationary_data/stationary_data_normalized_train.csv")    
parser.add_argument("--test_stationary_filename", type=str, default="stationary_data/stationary_data_normalized_test.csv")    
# parser.add_argument("--feature_ranking_path", type=str, default="saved_classical_ml_models/feature_impoerance_rf.csv")    

parser.add_argument("--mci_metadata", type=str, default="intermediate_files/mci_metadata.csv")  
parser.add_argument("--nonmci_metadata", type=str, default="intermediate_files/nonmci_metadata.csv")    


if parser.parse_args().viz_method == "tsne":
    args = parser.parse_args()
    vis_tools.tSNE_visualization(args.train_stationary_filename 
                                , args.test_stationary_filename     
                                , args.sampled     
                                , args.sample_size
                                , args.features_to_show
                                , args.perplex
                                , args.num_it
                                , args.lr_rate)
  
elif parser.parse_args().viz_method == "pca":
    args = parser.parse_args()
    vis_tools.pca_visualization(args.train_stationary_filename 
                                , args.test_stationary_filename     
                                , args.sampled     
                                , args.sample_size
                                , args.features_to_show
                                )   
elif parser.parse_args().viz_method == "none":
    print("Warning: no visualization method has been selected.")



if parser.parse_args().compute_table_1 == 1:
    args = parser.parse_args()
    vis_tools.compute_table_stats(args.train_stationary_filename 
                                , args.test_stationary_filename     
                                # , args.features_to_show
                                , args.mci_metadata     
                                , args.nonmci_metadata                                
                                # , args.feature_ranking_path                                
                                )
  
elif parser.parse_args().compute_table_1 == 0:
    print("Warning: no compute_table_1 method has been selected.")


if parser.parse_args().compute_table_progress_report == 1:
    args = parser.parse_args()
    vis_tools.compute_table_progress_report(args.train_stationary_filename 
                                , args.test_stationary_filename     
                                , args.features_to_show
                                , args.mci_metadata     
                                , args.nonmci_metadata                                
                                , args.feature_ranking_path                                
                                )
  
elif parser.parse_args().compute_table_progress_report == 0:
    print("Warning: no compute_table_progress_report method has been selected.")    



if parser.parse_args().plot_shap == 1:
    args = parser.parse_args()
    vis_tools.plot_shaps(args.train_stationary_filename 
                                , args.test_stationary_filename 
                                , args.trained_model_path     
                                )  

if parser.parse_args().plot_violins_flag == 1:
    args = parser.parse_args()
    vis_tools.plot_violins(args.train_stationary_filename 
                                , args.test_stationary_filename 
                                , args.feature_ranking_path     
                                , args.sampled     
                                , args.sample_size
                                )  

if parser.parse_args().descs == 1:
    args = parser.parse_args()
    vis_tools.extract_feature_descriptions(args.train_stationary_filename 
                                )  

if parser.parse_args().plot_surv == 1:
    args = parser.parse_args()
    vis_tools.plot_survival()  

if parser.parse_args().compute_p == 1:
    args = parser.parse_args()
    vis_tools.compute_p_values()  
