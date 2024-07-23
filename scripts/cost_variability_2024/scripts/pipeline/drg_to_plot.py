def drg_to_plot(my_drg):
    from drg_to_dat import drg_to_dat
    from tableone import TableOne
    from sklearn.impute import SimpleImputer
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    df = drg_to_dat(my_drg)
    
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
    Y = (Y - Y.mean()) / Y.std()

    # Fit a Random Forest model
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score, mean_squared_error
    from sklearn.model_selection import cross_val_score
    from scipy.stats import linregress

    # Instantiate the Random Forest model
    rf = RandomForestRegressor(n_estimators=1000,  
                                    min_samples_split=2,  
                                    min_samples_leaf=1, 
                                    max_depth=None,  
                                    max_features=1) 

    #from sklearn.linear_model import LinearRegression
    #rf = LinearRegression()

    #from sklearn.linear_model import Lasso, LassoCV
    #lasso_cv = LassoCV(alphas=[0.1, 0.01, 0.001, 0.0005, 0.0001], cv=5)
    #lasso_cv.fit(X_imputed, Y)
    #rf = lasso_model = Lasso(alpha=lasso_cv.alpha_)

    # Fit the model to your data
    rf.fit(X_imputed, Y)

    # Predict on the training set
    Y_pred = rf.predict(X_imputed)

    # Calculate R^2 on the training set
    r2_ori = r2_score(Y, Y_pred)

    # Calculate RMSE on the training set
    rmse_ori = mean_squared_error(Y, Y_pred, squared=False)

    ### Calibration plot

    # Predict values using the model on the training dataset
    Y_pred = rf.predict(X_imputed)

    # Define the quantiles
    quantiles = np.linspace(0, 1, 11)  # For quintiles

    # Determine the bin edges based on quantiles of Y_pred
    bin_edges = np.quantile(Y_pred, quantiles)[1:]

    # Use digitize to assign each Y_pred to a bin
    bins = np.digitize(Y_pred, bin_edges, right=True)

    # Initialize lists for plotting
    mean_predicted_ori = []
    mean_actual_ori = []

    # Calulate slope and intercept for the in-sample calibration curve
    slope_ori, intercept_ori, _, _, _ = linregress(Y_pred, Y)

    # Calculate mean actual and predicted values for each bin
    for i in range(1, len(bin_edges)):
        bin_indices = bins == i
        if np.any(bin_indices):
            mean_predicted_ori.append(Y_pred[bin_indices].mean())
            mean_actual_ori.append(Y[bin_indices].mean())

    # Plotting
    plt.figure(figsize=(10, 10))

    # Plot the perfect prediction line
    plt.plot([min(mean_actual_ori), max(mean_actual_ori)],
            [min(mean_actual_ori), max(mean_actual_ori)], 
            color='red', linestyle='--', label='Perfect Calibration')

    ###
    from sklearn.model_selection import KFold
    n_folds = 5 # No. of folds here
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)  

    r2_cv = []
    rmse_cv = []
    slope_cv = []
    intercept_cv = []

    # Loop over each fold
    for fold_i, (train_index, test_index) in enumerate(kf.split(X_imputed)):
        X_train, X_test = X_imputed[train_index], X_imputed[test_index]
        Y_train, Y_test = Y[train_index], Y[test_index]
        
        # Fit the model
        rf.fit(X_train, Y_train)
        
        # Predict on the test set
        Y_pred = rf.predict(X_test)
        
        # Calculate R^2 for the current fold
        r2 = r2_score(Y_test, Y_pred)
        r2_cv.append(r2)
        
        # Calculate RMSE for the current fold
        rmse = mean_squared_error(Y_test, Y_pred, squared=False)
        rmse_cv.append(rmse)
        
        # Calulate slope and intercept for the cv calibration curves
        slope, intercept, _, _, _ = linregress(Y_pred, Y_test)
        slope_cv.append(slope)
        intercept_cv.append(intercept)
        
        # Use digitize to assign each Y_pred to a bin
        bins = np.digitize(Y_pred, bin_edges, right=True)
        
        mean_predicted = []
        mean_actual = []
        
        # Calculate mean actual and predicted values for each bin
        for i in range(1, len(bin_edges) + 1):
            bin_indices = bins == i
            if np.any(bin_indices):
                mean_predicted.append(Y_pred[bin_indices].mean())
                mean_actual.append(Y_test[bin_indices].mean())
        
        # Plot the calibration curve for the current fold
        plt.plot(mean_predicted, mean_actual, linestyle='-', color='gray', alpha=0.5)

    # Plot the in-sample calibration curve
    plt.plot(mean_predicted_ori, mean_actual_ori, color='blue', label='In sample', marker='o')

    # Add labels for the legend
    plt.plot([], [], linestyle='-', color='gray', alpha=0.5, label='CV Folds')

    # Add text for the metric values
    plt.text(x=0.02, y=0.875, s=f'In-sample', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.85, s=f'$R^2$: {100*r2_ori:.1f}%', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.825, s=f'RMSE: {rmse_ori:.2f}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.8, s=f'Intercept: {intercept_ori:.2f}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.775, s=f'Slope: {slope_ori:.2f}', transform=plt.gca().transAxes, fontsize=12)

    plt.text(x=0.02, y=0.725, s=f'{n_folds}-fold CV', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.7, s=f'$R^2$: {100*np.mean(r2_cv):.2f}%', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.675, s=f'RMSE: {np.mean(rmse_cv):.2f}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.65, s=f'Intercept: {np.mean(intercept_cv):.2f}', transform=plt.gca().transAxes, fontsize=12)
    plt.text(x=0.03, y=0.625, s=f'Slope: {np.mean(slope_cv):.2f}', transform=plt.gca().transAxes, fontsize=12)

    plt.xlim([min(mean_actual_ori), max(mean_actual_ori)])
    plt.ylim([min(mean_actual_ori), max(mean_actual_ori)])
    plt.title(f"DRG ID {df.drg_id[0]}: {df.drg_name[0][:50]} (n={X_imputed.shape[0]})\nCross-Validated Calibration ({rf.__class__.__name__} model)")
    plt.xlabel('Mean Predicted Cost')
    plt.ylabel('Mean Observed Cost')
    plt.legend()
    plt.savefig(f'calplots/{100*np.mean(r2_cv):.0f}_{X_imputed.shape[0]}_{df.drg_id[0]}.pdf', format='pdf')
    plt.show()