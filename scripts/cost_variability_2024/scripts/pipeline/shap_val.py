import os
os.chdir('/Users/grolleau/Desktop/github repos/CDSS/scripts/cost_variability_2024/scripts/pipeline/')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

from drg_to_dat import drg_to_dat
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
from scipy.stats import fisher_exact, ttest_ind
from lightgbm import LGBMRegressor
from scipy.stats import randint, uniform, linregress
from scipy.interpolate import UnivariateSpline
from mapie.regression import MapieQuantileRegressor
from sklearn.model_selection import KFold, RandomizedSearchCV, train_test_split
from sklearn.metrics import r2_score, root_mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import SplineTransformer
import shap
import math

def ids_to_sql(ids): return f"({', '.join([str(int(i)) for i in ids])})"

def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
def my_round(x, k=3):
    if x > 10**-k:
        return str(np.round(x, k))
    else:
        return f"< 10^{-math.ceil(-math.log10(x)-1)}"

def drg_to_imp(my_drg):

    df = drg_to_dat(my_drg)

    drg_id = df.drg_id[0]
    drg_name = df.drg_name[0]

    if len(df) < 400:
        print(f"DRG ID {my_drg} has less than 400 patients")
        return # Skip DRGs with less than 400 patients

    # Keep only the rows/patients with features
    df = df[~df["anon_id_1"].isna()]

    # Drop the variable 'DummyFeature' as it all ones
    df = df.drop('DummyFeature', axis=1)

    # Drop all columns with only one unique value (Nan)
    df = df.drop(columns=list(df.columns[df.isna().all()]))

    ### Data description

    # Where is located the first feature
    first_feat_pos = df.columns.get_loc("anon_id_1") + 1

    # Select columns with only one unique value (eg. 'race_Non-Hispanic', 'race_White', 'sex_Female', etc.)
    columns_with_one_unique_value = df.columns[df.nunique() == 1]

    # Replace NaN values in these columns with 0
    df.loc[:, columns_with_one_unique_value] = df.loc[:, columns_with_one_unique_value].fillna(0)

    # Create Table 1
    feat_0p_names = list(df.columns[first_feat_pos:])[0:15]

    # Sort features by number of missing values
    sorted_features_names = list(df.loc[:,df.columns[first_feat_pos:]].isna().sum().sort_values().index)

    ### Data preparation

    # Keep only the features
    X = df.iloc[:, 1+first_feat_pos:] # (1+ because we added the 'Cost_Adj_Quantiles' column)

    # Get variable names
    var_names = X.columns.tolist()
    var_names += [e + "_mis" for e in var_names]

    # Cbind a mask for missing values
    X = pd.concat([X, X.isna()], axis=1)

    # Create an imputer object with a strategy of 'most_frequent' to impute by the mode
    imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')

    # Fit the imputer to the data and transform it
    X_imputed = pd.DataFrame(imputer.fit_transform(X))
        
    # Boolean vector for features with non-unique values
    non_unique_feat = X_imputed.apply(lambda x: x.nunique()>1, axis=0) 

    # Keep only the features with non-unique values
    X_imputed = np.array(X_imputed.loc[:, non_unique_feat]).astype(float)

    # Update var_names, removing the features with non-unique values
    var_names = [var_names[i] for i in range(len(var_names)) if non_unique_feat[i]]

    # Normalize the features
    X_imputed = (X_imputed - X_imputed.mean(axis=0)) / X_imputed.std(axis=0)

    # Keep only the target
    Y = np.array(df["Cost_Direct_Scaled"])

    # Normalize the target
    Y_mean = Y.mean(); Y_std = Y.std()
    Y = (Y - Y_mean) / Y_std
    
    return X_imputed, Y, Y_mean, Y_std, drg_id, drg_name, var_names, df['observation_id']

class pipeline:
    def __init__(self, my_drg, alpha_ci = .5):
        self.my_drg = my_drg
        self.alpha_ci = alpha_ci        
        
    def fit(self):
        X_imputed, Y, Y_mean, Y_std, drg_id, drg_name, var_names, observation_id = drg_to_imp(self.my_drg) #2334 # 2392

        random_state = 18

        X_train, X_test, y_train, y_test, ob_train, ob_test = train_test_split(X_imputed, Y, observation_id, test_size=.25, random_state=random_state)
        X_train, X_calib, y_train, y_calib, ob_train, _ = train_test_split(X_train, y_train, ob_train, test_size=.15, random_state=random_state)

        estimator = LGBMRegressor(
            objective='quantile',
            alpha=0.5,
            verbose=-1,
            random_state=random_state
        )

        params_distributions = dict(
            num_leaves=randint(low=10, high=50),
            max_depth=randint(low=3, high=20),
            n_estimators=randint(low=50, high=100),
            learning_rate=uniform()
        )

        optim_model = RandomizedSearchCV(
            estimator,
            param_distributions=params_distributions,
            n_jobs=-1,
            n_iter=10,
            cv=KFold(n_splits=5, shuffle=True),
            random_state=random_state
        )

        optim_model.fit(X_train, y_train)
        estimator = optim_model.best_estimator_

        mapie_reg = MapieQuantileRegressor(estimator, method = "quantile", cv = "split", alpha=self.alpha_ci)

        mapie_reg.fit(
            X_train,
            y_train,
            X_calib=X_calib,
            y_calib=y_calib,
            random_state=random_state
        )
        y_pred, y_pis = mapie_reg.predict(X_test)
        ub = y_pis[:, 1, 0]
        lb = y_pis[:, 0, 0]
        ciw = ub - lb

        # Calculate R^2 on the training set
        r2_test = r2_score(y_test, y_pred)

        # Calculate RMSE on the training set
        rmse_test = root_mean_squared_error(y_test, y_pred)

        # Calculate slope and intercept for the in-sample calibration curve
        slope_test, intercept_test, _, _, _ = linregress(y_pred, y_test)

        # set negative intervals to zero
        ciw[ciw < 0] = 0

        # Denormalize the targets
        y_pred = y_pred * Y_std + Y_mean
        y_test = y_test * Y_std + Y_mean

        # Denormalize the CI bounds
        lb = lb * Y_std + Y_mean
        ub = ub * Y_std + Y_mean

        # Denormalize the CIw
        ciw *= Y_std

        # Normalize y_test values for color mapping
        norm = mcolors.Normalize(vmin=min(ciw), vmax=max(ciw))

        # Create scatter plot
        plt.scatter(y_pred, y_test, c=ciw, cmap='coolwarm', norm=norm)

        # Add a diagonal line behind all dots
        # Determine the range for the diagonal line

        lims = [
            np.min([plt.gca().get_xlim(), plt.gca().get_ylim()]),  # min of both axes
            np.max([plt.gca().get_xlim(), plt.gca().get_ylim()]),  # max of both axes
        ]
        plt.plot(lims, lims, color='black', label='Perfect Calibration')

        # Fit a spline to the data
        spline_model = make_pipeline(
            SplineTransformer(degree = 1), # adjust the degree of the spline here
            LinearRegression()
        )
        spline_model.fit(y_pred.reshape(-1, 1), y_test)
        x_space = np.linspace(lims[0], lims[1], 100)
        y_line = spline_model.predict(x_space.reshape(-1, 1))

        # Add the line to the plot
        plt.plot(x_space, y_line, linestyle='--', color='black', label='Calibration Curve')

        # Add a colorbar to show the mapping from y_test values to colors
        plt.colorbar(label='Prediction Interval Length (CQR)')

        # Add labels and title (optional)
        plt.xlabel('Predicted Cost')
        plt.ylabel('Observed Cost\n(Cost_Direct_Scaled)')
        plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nPredicted vs. Observed Cost vs Uncertainty in Predictions\nEvaluating fine-tuned {estimator.__class__.__name__} on test set  (n={y_test.shape[0]})")

        # Set xlim and ylim
        plt.xlim(np.quantile(y_test, (.05, .95)))
        plt.ylim(np.quantile(y_test, (.05, .95)))

        plt.text(x=0.60, y=0.25, s=f'Test performance', transform=plt.gca().transAxes, fontsize=12)
        plt.text(x=0.65, y=0.2, s=f'$R^2$: {100*np.mean(r2_test):.2f}%', transform=plt.gca().transAxes, fontsize=10)
        plt.text(x=0.65, y=0.15, s=f'RMSE: {np.mean(rmse_test):.2f}', transform=plt.gca().transAxes, fontsize=10)
        plt.text(x=0.65, y=0.1, s=f'Intercept: {np.mean(intercept_test):.2f}', transform=plt.gca().transAxes, fontsize=10)
        plt.text(x=0.65, y=0.05, s=f'Slope: {np.mean(slope_test):.2f}', transform=plt.gca().transAxes, fontsize=10)

        plt.legend(loc='upper left')
        
        make_folder(f'res/res_{100*self.alpha_ci:.0f}/LGBM_eval')
        plt.savefig(f'res/res_{100*self.alpha_ci:.0f}/LGBM_eval/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)
        plt.show()

        ####
        # Step 1: Sort y_pred and ciw together based on y_pred values
        indices = np.argsort(y_pred)
        sorted_y_pred = y_pred[indices]
        sorted_ciw = ciw[indices]
        sorted_lb = lb[indices]
        sorted_ub = ub[indices]

        # Step 2: Divide sorted_y_pred into fifths
        fifths = np.array_split(sorted_y_pred, 5)
        ciw_fifths = np.array_split(sorted_ciw, 5)
        lb_fifths = np.array_split(sorted_lb, 5)
        ub_fifths = np.array_split(sorted_ub, 5)

        # Step 3: Calculate mean ciw for each fifth
        mean_ciw_per_fifth = [np.mean(fifth) for fifth in ciw_fifths]
        mean_lb_per_fifth = [np.mean(fifth) for fifth in lb_fifths]
        mean_ub_per_fifth = [np.mean(fifth) for fifth in ub_fifths]

        # Step 4: Calculate std ciw for each fifth
        std_ciw_per_fifth = [np.std(fifth)/np.sqrt(len(fifth)) for fifth in ciw_fifths]
        std_lb_per_fifth = [np.std(fifth)/np.sqrt(len(fifth)) for fifth in lb_fifths]
        std_ub_per_fifth = [np.std(fifth)/np.sqrt(len(fifth)) for fifth in ub_fifths]

        # Prepare the labels for the plot
        bins = []; labels = []
        for i, mean_ciw in enumerate(mean_ciw_per_fifth):
            bins.append((np.min(fifths[i]), np.max(fifths[i])))
            labels.append(f"{bins[-1][0]:.1f} to {bins[-1][1]:.1f}")

        plt.figure(figsize=(10, 10))

        # Adjusted plot code to include error bars for all variables
        width = 0.25  # Width of the bars
        positions = np.arange(len(mean_ciw_per_fifth))  # Base positions for each group of bars

        # Plotting Mean PI lower bound
        plt.bar(positions - width, mean_lb_per_fifth, width=width, label='Mean PI Lower Bound', yerr=std_lb_per_fifth, capsize=3)

        # Plotting Mean PI length
        plt.bar(positions, mean_ciw_per_fifth, width=width, label='Mean PI Length', yerr=std_ciw_per_fifth, capsize=3)

        # Plotting Mean PI upper bound
        plt.bar(positions + width, mean_ub_per_fifth, width=width, label='Mean PI Upper Bound', yerr=std_ub_per_fifth, capsize=3)

        # Add labels under bars
        plt.xticks(positions, labels, rotation=0)

        # Adding labels and title for clarity
        plt.legend()
        plt.xlabel('Predicted Cost\n(Categorized by Fifths)')
        plt.ylabel(f'{100*(1-self.alpha_ci):.0f}% CQR Prediction Intervals')
        plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nUncertainty in the Predicted Costs\nFrom Conformalized Quantile Regression ({estimator.__class__.__name__} on test set [n={y_test.shape[0]}])")

        plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nUncertainty in the Predicted Costs\nFrom Conformalized Quantile Regression ({estimator.__class__.__name__} on test set [n={y_test.shape[0]}])")

        make_folder(f"res/res_{100*self.alpha_ci:.0f}/uncertainty_in_predicted_costs")
        plt.savefig(f'res/res_{100*self.alpha_ci:.0f}/uncertainty_in_predicted_costs/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)

        # Show the plot
        plt.show()

        #### Shap values ####

        # Fits the explainer
        X = pd.DataFrame(X_imputed, columns=var_names)

        explainer = shap.Explainer(estimator.predict, X)

        # Calculates the SHAP values - It takes some time
        shap_values = explainer(X, max_evals=1000)

        # Plot the SHAP values
        shap.plots.beeswarm(shap_values, show = False)
        plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nBeeswarm plot for the {estimator.__class__.__name__} model")
        
        make_folder(f"res/res_{100*self.alpha_ci:.0f}/shap")
        plt.savefig(f'res/res_{100*self.alpha_ci:.0f}/shap/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)
        plt.show()
        
        # Check outliers in all data using the conformalized PI    
        _, y_pis_all = mapie_reg.predict(X_imputed)
        ub_all = y_pis_all[:, 1, 0]
        lb_all = y_pis_all[:, 0, 0]
        
        # Compare outliers vs not only in the test set
        #cqr_t = np.maximum(y_pis[:, 1, 0], y_pis[:, 0, 0]) * Y_std + Y_mean
        #hi_than_pred = y_test > cqr_t #resid > quartile
        #ob_out, ob_not = ob_test[hi_than_pred], ob_test[~hi_than_pred]
        
        # Get the CQR upper bound threshold        
        hi_than_pred = Y > np.maximum(ub_all, lb_all)
        ob_out, ob_not = observation_id[hi_than_pred], observation_id[~hi_than_pred]
        
        def folder_exp(ids_tup, comp, out='hi'):
            make_folder(f"res/res_{out}_{100*self.alpha_ci:.0f}/{comp.__name__}")
            comp_by_ids(ids_tup, comp).to_csv(f"res/res_{out}_{100*self.alpha_ci:.0f}/{comp.__name__}/drg_{drg_id}.csv", index=False)
            
        folder_exp((ob_not, ob_out), comp_med, out='hi')
        folder_exp((ob_not, ob_out), comp_proc, out='hi')
        folder_exp((ob_not, ob_out), comp_diag, out='hi')
        folder_exp((ob_not, ob_out), comp_medorderset, out='hi')
        folder_exp((ob_not, ob_out), comp_procorderset, out='hi')
            
        # Top 20 meds for positive vs negative residuals (ie higher than predicted vs lower than predicted)
        make_folder(f"res/res_{100*self.alpha_ci:.0f}/top_med")
        top_20_med_by_ids((ob_not, ob_out)).to_csv(f"res/res_{100*self.alpha_ci:.0f}/top_med/drg_{drg_id}.csv", index=False) 
        
        # Compare hours of admission for positive vs negative residuals
        self.comp_hours_by_ids((ob_not, ob_out), drg_id, drg_name)
        
        # Get the CQR lower bound threshold        
        lo_than_pred = Y < np.minimum(ub_all, lb_all)
        ob_out, ob_not = observation_id[lo_than_pred], observation_id[~lo_than_pred]
        folder_exp((ob_not, ob_out), comp_med, out='lo')
        folder_exp((ob_not, ob_out), comp_proc, out='lo')
        folder_exp((ob_not, ob_out), comp_diag, out='lo')
        folder_exp((ob_not, ob_out), comp_medorderset, out='lo')
        folder_exp((ob_not, ob_out), comp_procorderset, out='lo')
        
    def comp_hours_by_ids(self, ids_tup, drg_id, drg_name):
        # Instantiate a client object so you can make queries
        client = bigquery.Client()

        # Create a connexion to that client
        conn = dbapi.connect(client)

        dfs = []
        for it, ids in enumerate(ids_tup):
            comp_hours_query = f"""
            SELECT EXTRACT(HOUR FROM event_time_jittered) AS hour 
            FROM `som-nero-phi-jonc101.shc_core_2023.adt`
            WHERE event_type = 'Admission' AND pat_enc_csn_id_coded IN {ids_to_sql(ids_tup[it])}
            """
            df = pd.read_sql_query(comp_hours_query, conn)
            if it == 0:
                df.columns = [f"{col}_not" for col in df.columns]
            else:
                df.columns = [f"{col}_out" for col in df.columns]
            dfs.append(df)
        df = pd.concat(dfs, axis=1)

        # Define bin edges
        bins = np.array(range(0, 25))-.5

        # Plotting
        plt.figure(figsize=(10, 10))

        # Histogram for hour_not with proportions
        plt.hist(df['hour_not'], bins=bins, density=True, color='blue', alpha=0.5, label='Cost lower than predicted')

        # Histogram for hour_out with proportions
        plt.hist(df['hour_out'], bins=bins, density=True, color='green', alpha=0.5, label='Cost higher than predicted')

        p_val = ttest_ind(df['hour_not'].dropna(), df['hour_out'].dropna())[1]
        mean_not = df['hour_not'].mean(); sd_not = df['hour_not'].std()
        mean_out = df['hour_out'].mean(); sd_out = df['hour_out'].std()
        
        plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nTime of Admissions:\nCost higher (mean={mean_out:.1f}; sd={sd_out:.1f}) vs lower (mean={mean_not:.1f}; sd={sd_not:.1f}) than predicted (p={p_val:.3f})")
        plt.xlabel('Hour of Admission')
        plt.ylabel('Proportion of Admissions')
        plt.legend()

        # Set x-axis labels to 1 through 24
        plt.xticks(range(0, 24))

        plt.tight_layout()
        make_folder(f"res/res_{100*self.alpha_ci:.0f}/hours")
        plt.savefig(f'res/res_{100*self.alpha_ci:.0f}/hours/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)
        plt.show()
    
def top_20_med_by_ids(ids_tup):

    # Instantiate a client object so you can make queries
    client = bigquery.Client()

    # Create a connexion to that client
    conn = dbapi.connect(client)

    dfs = []
    for it, ids in enumerate(ids_tup):
        med_query = f"""
        SELECT med_description, COUNT(pat_enc_csn_id_coded) as n_pat, SUM(n_pres) as n_pres
        FROM
        (
        SELECT med_description, pat_enc_csn_id_coded, COUNT(*) as n_pres
        FROM `som-nero-phi-jonc101.shc_core_2023.order_med`
        WHERE pat_enc_csn_id_coded in {ids_to_sql(ids)}
        GROUP BY med_description, pat_enc_csn_id_coded
        )
        GROUP BY med_description
        ORDER BY n_pat DESC, med_description
        LIMIT 20
        """

        df = pd.read_sql_query(med_query, conn)
        df.insert(1, 'frac_pat', df['n_pat'] / len(ids))
        df.insert(2, 'avg_n_pres', df['n_pres'] / len(ids))
        if it == 0:
            df.columns = [f"{col}_not" for col in df.columns]
        else:
            df.columns = [f"{col}_out" for col in df.columns]
        dfs.append(df)
    return pd.concat(dfs, axis=1)

def comp_med(ids_tup):
    query = f"""
    WITH lo_tab as 
    (
    SELECT med_description, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[0])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT med_description, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.order_med`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[0])}
    GROUP BY med_description, pat_enc_csn_id_coded
    )
    GROUP BY med_description
    ORDER BY n_pat DESC, med_description
    ),

    hi_tab as
    (
    SELECT med_description, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[1])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT med_description, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.order_med`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[1])}
    GROUP BY med_description, pat_enc_csn_id_coded
    )
    GROUP BY med_description
    ORDER BY n_pat DESC, med_description
    ),

    comp_tab as 
    (
    SELECT hi_tab.med_description,
   ROUND(hi_tab.n_pat / (hi_tab.n_pat + hi_tab.no_ttt), 3) as frac_out,
    hi_tab.n_pat as n_pat_out, hi_tab.no_ttt as no_ttt_out, hi_tab.n_pres as n_pres_out,
    ROUND(lo_tab.n_pat / (lo_tab.n_pat + lo_tab.no_ttt), 3) as frac_not,
    lo_tab.n_pat as n_pat_not, lo_tab.no_ttt as no_ttt_not, lo_tab.n_pres as n_pres_not,
    FROM hi_tab INNER JOIN lo_tab
    ON hi_tab.med_description = lo_tab.med_description
    ORDER BY med_description
    )

    SELECT *,
    CASE 
        WHEN no_ttt_out * n_pat_not = 0 THEN NULL
        ELSE ROUND((n_pat_out * no_ttt_not) / (no_ttt_out * n_pat_not), 2)
    END as odds_ratio
    FROM comp_tab
    ORDER BY odds_ratio DESC
    """
    return query

def comp_proc(ids_tup):
    query = f"""
    WITH lo_tab as 
    (
    SELECT description, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[0])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT description, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.order_proc`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[0])}
    GROUP BY description, pat_enc_csn_id_coded
    )
    GROUP BY description
    ORDER BY n_pat DESC, description
    ),

    hi_tab as
    (
    SELECT description, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[1])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT description, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.order_proc`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[1])}
    GROUP BY description, pat_enc_csn_id_coded
    )
    GROUP BY description
    ORDER BY n_pat DESC, description
    ),

    comp_tab as 
    (
    SELECT hi_tab.description,
   ROUND(hi_tab.n_pat / (hi_tab.n_pat + hi_tab.no_ttt), 3) as frac_out,
    hi_tab.n_pat as n_pat_out, hi_tab.no_ttt as no_ttt_out, hi_tab.n_pres as n_pres_out,
    ROUND(lo_tab.n_pat / (lo_tab.n_pat + lo_tab.no_ttt), 3) as frac_not,
    lo_tab.n_pat as n_pat_not, lo_tab.no_ttt as no_ttt_not, lo_tab.n_pres as n_pres_not,
    FROM hi_tab INNER JOIN lo_tab
    ON hi_tab.description = lo_tab.description
    ORDER BY description
    )

    SELECT *,
    CASE 
        WHEN no_ttt_out * n_pat_not = 0 THEN NULL
        ELSE ROUND((n_pat_out * no_ttt_not) / (no_ttt_out * n_pat_not), 2)
    END as odds_ratio
    FROM comp_tab
    ORDER BY odds_ratio DESC
    """
    return query

def comp_diag(ids_tup):
    query = f"""
    WITH lo_tab as 
    (
    SELECT dx_name, COUNT(pat_enc_csn_id_jittered) as n_pat, {len(ids_tup[0])} - COUNT(pat_enc_csn_id_jittered) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT dx_name, pat_enc_csn_id_jittered, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.diagnosis`
    WHERE pat_enc_csn_id_jittered in {ids_to_sql(ids_tup[0])}
    GROUP BY dx_name, pat_enc_csn_id_jittered
    )
    GROUP BY dx_name
    ORDER BY n_pat DESC, dx_name
    ),

    hi_tab as
    (
    SELECT dx_name, COUNT(pat_enc_csn_id_jittered) as n_pat, {len(ids_tup[1])} - COUNT(pat_enc_csn_id_jittered) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT dx_name, pat_enc_csn_id_jittered, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.diagnosis`
    WHERE pat_enc_csn_id_jittered in {ids_to_sql(ids_tup[1])}
    GROUP BY dx_name, pat_enc_csn_id_jittered
    )
    GROUP BY dx_name
    ORDER BY n_pat DESC, dx_name
    ),

    comp_tab as 
    (
    SELECT hi_tab.dx_name,
   ROUND(hi_tab.n_pat / (hi_tab.n_pat + hi_tab.no_ttt), 3) as frac_out,
    hi_tab.n_pat as n_pat_out, hi_tab.no_ttt as no_ttt_out, hi_tab.n_pres as n_pres_out,
    ROUND(lo_tab.n_pat / (lo_tab.n_pat + lo_tab.no_ttt), 3) as frac_not,
    lo_tab.n_pat as n_pat_not, lo_tab.no_ttt as no_ttt_not, lo_tab.n_pres as n_pres_not,
    FROM hi_tab INNER JOIN lo_tab
    ON hi_tab.dx_name = lo_tab.dx_name
    ORDER BY dx_name
    )

    SELECT *,
    CASE 
        WHEN no_ttt_out * n_pat_not = 0 THEN NULL
        ELSE ROUND((n_pat_out * no_ttt_not) / (no_ttt_out * n_pat_not), 2)
    END as odds_ratio
    FROM comp_tab
    ORDER BY odds_ratio DESC
    """
    return query

def comp_medorderset(ids_tup):
    query = f"""
        WITH lo_tab as 
    (
    SELECT protocol_name, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[0])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT protocol_name, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.med_orderset`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[0])}
    GROUP BY protocol_name, pat_enc_csn_id_coded
    )
    GROUP BY protocol_name
    ORDER BY n_pat DESC, protocol_name
    ),

    hi_tab as
    (
    SELECT protocol_name, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[1])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT protocol_name, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.med_orderset`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[1])}
    GROUP BY protocol_name, pat_enc_csn_id_coded
    )
    GROUP BY protocol_name
    ORDER BY n_pat DESC, protocol_name
    ),

    comp_tab as 
    (
    SELECT hi_tab.protocol_name,
   ROUND(hi_tab.n_pat / (hi_tab.n_pat + hi_tab.no_ttt), 3) as frac_out,
    hi_tab.n_pat as n_pat_out, hi_tab.no_ttt as no_ttt_out, hi_tab.n_pres as n_pres_out,
    ROUND(lo_tab.n_pat / (lo_tab.n_pat + lo_tab.no_ttt), 3) as frac_not,
    lo_tab.n_pat as n_pat_not, lo_tab.no_ttt as no_ttt_not, lo_tab.n_pres as n_pres_not,
    FROM hi_tab INNER JOIN lo_tab
    ON hi_tab.protocol_name = lo_tab.protocol_name
    ORDER BY protocol_name
    )

    SELECT *,
    CASE 
        WHEN no_ttt_out * n_pat_not = 0 THEN NULL
        ELSE ROUND((n_pat_out * no_ttt_not) / (no_ttt_out * n_pat_not), 2)
    END as odds_ratio
    FROM comp_tab
    ORDER BY odds_ratio DESC
    """
    return query

def comp_procorderset(ids_tup):
    query = f"""
        WITH lo_tab as 
    (
    SELECT protocol_name, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[0])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT protocol_name, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.proc_orderset`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[0])}
    GROUP BY protocol_name, pat_enc_csn_id_coded
    )
    GROUP BY protocol_name
    ORDER BY n_pat DESC, protocol_name
    ),

    hi_tab as
    (
    SELECT protocol_name, COUNT(pat_enc_csn_id_coded) as n_pat, {len(ids_tup[1])} - COUNT(pat_enc_csn_id_coded) as no_ttt, SUM(n_pres) as n_pres
    FROM
    (
    SELECT protocol_name, pat_enc_csn_id_coded, COUNT(*) as n_pres
    FROM `som-nero-phi-jonc101.shc_core_2023.proc_orderset`
    WHERE pat_enc_csn_id_coded in {ids_to_sql(ids_tup[1])}
    GROUP BY protocol_name, pat_enc_csn_id_coded
    )
    GROUP BY protocol_name
    ORDER BY n_pat DESC, protocol_name
    ),

    comp_tab as 
    (
    SELECT hi_tab.protocol_name,
   ROUND(hi_tab.n_pat / (hi_tab.n_pat + hi_tab.no_ttt), 3) as frac_out,
    hi_tab.n_pat as n_pat_out, hi_tab.no_ttt as no_ttt_out, hi_tab.n_pres as n_pres_out,
    ROUND(lo_tab.n_pat / (lo_tab.n_pat + lo_tab.no_ttt), 3) as frac_not,
    lo_tab.n_pat as n_pat_not, lo_tab.no_ttt as no_ttt_not, lo_tab.n_pres as n_pres_not,
    FROM hi_tab INNER JOIN lo_tab
    ON hi_tab.protocol_name = lo_tab.protocol_name
    ORDER BY protocol_name
    )

    SELECT *,
    CASE 
        WHEN no_ttt_out * n_pat_not = 0 THEN NULL
        ELSE ROUND((n_pat_out * no_ttt_not) / (no_ttt_out * n_pat_not), 2)
    END as odds_ratio
    FROM comp_tab
    ORDER BY odds_ratio DESC
    """
    return query

def comp_by_ids(ids_tup, comp_query_fun):

    # Instantiate a client object so you can make queries
    client = bigquery.Client()

    # Create a connexion to that client
    conn = dbapi.connect(client)

    comp_query = comp_query_fun(ids_tup)

    df = pd.read_sql_query(comp_query, conn)
    df['fisher_pval'] = df.apply(lambda x: my_round(fisher_exact([[x['n_pat_out'], x['no_ttt_out']], [x['n_pat_not'], x['no_ttt_not']]], alternative='two-sided')[1]), axis=1)
    df = df.sort_values(by='odds_ratio', ascending=False)
    return df

# test with one drg
#drg_to_cqr_shap(2392)#2334)
pipeline(my_drg=2392, alpha_ci= .5).fit()
pipeline(my_drg=2334, alpha_ci= .5).fit()