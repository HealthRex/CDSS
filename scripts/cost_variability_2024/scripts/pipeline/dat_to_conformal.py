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

    # Normalize the features
    X_imputed = (X_imputed - X_imputed.mean(axis=0)) / X_imputed.std(axis=0)

    # Keep only the target
    Y = np.array(df["Cost_Direct_Scaled"])

    # Normalize the target
    Y_mean = Y.mean(); Y_std = Y.std()
    Y = (Y - Y_mean) / Y_std
    
    return X_imputed, Y, Y_mean, Y_std, drg_id, drg_name

def drg_to_cqr(my_drg):
    X_imputed, Y, Y_mean, Y_std, drg_id, drg_name = drg_to_imp(my_drg) #2334 # 2392

    import numpy as np
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

    X_train, X_test, y_train, y_test = train_test_split(X_imputed, Y, test_size=.25, random_state=random_state)
    X_train, X_calib, y_train, y_calib = train_test_split(X_train, y_train, test_size=.15, random_state=random_state)

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
    ciw = y_pis[:, 1, 0] - y_pis[:, 0, 0]

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
        SplineTransformer(degree = 2), # adjust the degree of the spline here
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
    # Step 1: Sort y_test and ciw together based on y_test values
    indices = np.argsort(y_test)
    sorted_y_test = y_test[indices]
    sorted_ciw = ciw[indices]

    # Step 2: Divide sorted_y_test into fifths
    fifths = np.array_split(sorted_y_test, 5)
    ciw_fifths = np.array_split(sorted_ciw, 5)

    # Step 3: Calculate mean ciw for each fifth
    mean_ciw_per_fifth = [np.mean(fifth) for fifth in ciw_fifths]

    # Print the mean ciw for each fifth
    bins = []; labels = []
    for i, mean_ciw in enumerate(mean_ciw_per_fifth):
        print(f"Mean ciw for fifth {i+1} ({np.min(sorted_y_test[i]):.2f} to {np.max(sorted_y_test[i]):.2f}): {mean_ciw:.2f}")
        bins.append((np.min(fifths[i]), np.max(fifths[i])))
        labels.append(f"{bins[-1][0]:.1f} to {bins[-1][1]:.1f}")

    # Create the histogram
    plt.bar(range(len(mean_ciw_per_fifth)), mean_ciw_per_fifth, width=0.5, tick_label=labels)

    # Adding labels and title for clarity
    plt.xlabel('Observed Cost\n(Categorized by Fifths)')
    plt.ylabel('Mean CQR Prediction Interval Length')
    plt.title(f"DRG ID {drg_id}: {drg_name[:40]}\nUncertainty in the Predicted Costs\nFrom Conformalized Quantile Regression ({estimator.__class__.__name__} on test set [n={y_test.shape[0]}])")

    plt.savefig(f'uncertainty_in_predicted_costs/drg_{drg_id}.pdf', format='pdf', bbox_inches='tight', pad_inches=0.5)
    # Show the plot
    plt.show()
    
# Push pdfs to github