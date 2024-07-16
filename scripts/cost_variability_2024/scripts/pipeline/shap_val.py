import os
os.chdir('/Users/grolleau/Desktop/github repos/CDSS/scripts/cost_variability_2024/scripts/pipeline/')

def drg_to_imp(my_drg):
    from drg_to_dat import drg_to_dat
    from sklearn.impute import SimpleImputer
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

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

    # Four quantiles of cost 
    #q = 4
    #quantiles_data = pd.qcut(df['Cost_Direct_Scaled'], q, labels=[f"Q{i+1}" for i in range(q)])
    #df.insert(1, 'Cost_Adj_Quantiles', quantiles_data)

    #table1 = TableOne(df, columns=sorted_features_names, groupby='Cost_Adj_Quantiles', pval=True)
    #print(table1.tabulate(tablefmt="github"))

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

def drg_to_cqr_shap(my_drg):
    X_imputed, Y, Y_mean, Y_std, drg_id, drg_name, var_names, observation_id = drg_to_imp(my_drg) #2334 # 2392

    import numpy as np
    import pandas as pd
    from lightgbm import LGBMRegressor
    from scipy.stats import randint, uniform, linregress
    from scipy.interpolate import UnivariateSpline
    from mapie.regression import MapieQuantileRegressor
    from sklearn.model_selection import KFold, RandomizedSearchCV, train_test_split
    from sklearn.metrics import r2_score, root_mean_squared_error
    from sklearn.pipeline import make_pipeline
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import SplineTransformer

    random_state = 18

    X_train, X_test, y_train, y_test, ob_train, ob_test = train_test_split(X_imputed, Y, observation_id, test_size=.25, random_state=random_state)
    X_train, X_calib, y_train, y_calib, ob_train, ob_calib = train_test_split(X_train, y_train, ob_train, test_size=.15, random_state=random_state)

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

    mapie_reg = MapieQuantileRegressor(estimator, method = "quantile", cv = "split", alpha=0.1)

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

    ###
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

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
    plt.savefig(f'LGBM_eval/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)
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
    plt.ylabel('90% CQR Prediction Intervals')
    plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nUncertainty in the Predicted Costs\nFrom Conformalized Quantile Regression ({estimator.__class__.__name__} on test set [n={y_test.shape[0]}])")

    plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nUncertainty in the Predicted Costs\nFrom Conformalized Quantile Regression ({estimator.__class__.__name__} on test set [n={y_test.shape[0]}])")

    plt.savefig(f'uncertainty_in_predicted_costs/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)

    # Show the plot
    plt.show()

    #### Shap values ####
    import shap

    # Fits the explainer
    X = pd.DataFrame(X_imputed, columns=var_names)

    explainer = shap.Explainer(estimator.predict, X)

    # Calculates the SHAP values - It takes some time
    shap_values = explainer(X, max_evals=1000)

    # Plot the SHAP values
    shap.plots.beeswarm(shap_values, show = False)
    plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nBeeswarm plot for the {estimator.__class__.__name__} model")
    plt.savefig(f'shap/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)
    plt.show()
    
    ### Residuals for top medicines ###
    resid = y_test - y_pred
    hi_than_pred = resid > 0
    ob_hi, ob_lo = ob_test[hi_than_pred], ob_test[~hi_than_pred]
    top_20_med_by_ids((ob_lo, ob_hi)).to_csv(f"top_med/drg_{drg_id}.csv", index=False) 
    
def top_20_med_by_ids(ids_tup):
    def ids_to_sql(ids): return f"({', '.join([str(int(i)) for i in ids])})"

    from google.cloud import bigquery
    from google.cloud.bigquery import dbapi
    import os
    import pandas as pd

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
    os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

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
            df.columns = [f"{col}_lo" for col in df.columns]
        else:
            df.columns = [f"{col}_hi" for col in df.columns]
        dfs.append(df)
    return pd.concat(dfs, axis=1)