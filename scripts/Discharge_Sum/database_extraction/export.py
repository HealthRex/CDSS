import pandas as pd

# Read pickle file
df = pd.read_pickle('../exports/final_df_res.pkl')

# Take examples with non null "history and physical" AND "progress notes"
export_df = df[~df["h&p"].isnull() & ~df["progress_notes"].isnull()].iloc[:, 1:129]

# Drop the column named 'd_c_summaries' and 'd_c_sum_truncation' and 'jittered_date_d_c_summaries'
export_df.drop(columns=['d_c_summaries', 'd_c_sum_truncation', 'jittered_date_d_c_summaries'], inplace=True)

# remame the column 'truncated_d_c_summaries' to 'discharge_sumarry'
export_df.rename(columns={'truncated_d_c_summaries': 'discharge_summary'}, inplace=True)

# Place the column "h&p" in position 0 and "h&p_interval" in position 1
columns = list(export_df.columns)
columns.insert(0, columns.pop(columns.index('h&p')))
columns.insert(1, columns.pop(columns.index('h&p_interval')))
export_df = export_df[columns]

# Add a title column as the first column
export_df.insert(0, 'title', ["Patient trajectory no. " + str(i+1) for i in range(len(export_df))])

# Export to csv for google form creation
export_df.to_csv('../exports/export_df.csv', index=False)