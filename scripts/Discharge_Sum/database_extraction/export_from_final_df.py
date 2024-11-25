# Load the final_df from pickle
import pandas as pd
final_df = pd.read_pickle('../pickle/final_df.pkl')

# Take a few examples
export_df = final_df#.iloc[:100]

# Take only the columns "mrn" and "unjittered_date_d_c_summaries"
export_no_notes_df = export_df[["mrn", "unjittered_date_d_c_summaries"]]

# Add a title column as the first column
export_no_notes_df.insert(0, 'Title', ["Patient trajectory no. " + str(i+1) for i in range(len(export_df))])

# Reformat the date column
export_no_notes_df['unjittered_date_d_c_summaries'] = export_no_notes_df['unjittered_date_d_c_summaries'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Change the column names
export_no_notes_df = export_no_notes_df.rename(columns={"mrn": "Patient MRN", "unjittered_date_d_c_summaries": "Discharge summary creation date"})

# Remove seconds from the date
export_no_notes_df['Discharge summary creation date'] = export_no_notes_df['Discharge summary creation date'].str[:-3]

# Convert all columns to string
export_no_notes_df = export_no_notes_df.astype(str)

# Export to csv for google form creation
export_no_notes_df.to_csv('../exports/export_no_notes_df.csv', index=False)

# Drop the columns "unjittered_date_d_c_summaries" and "d_c_sum_truncation"
export_df = export_df.drop(columns=["unjittered_date_d_c_summaries", "d_c_sum_truncation"])

# Rename the column "truncated_d_c_summaries" to "discharge_summary"
export_df = export_df.rename(columns={"truncated_d_c_summaries": "discharge_summary"})

# put the columns 'h&p', 'h&p_interval', 'clinic_h&p_exam_and_progress_records', 'interval_h&p_note' in position 2, 3, 4, 5
# Columns to move
columns_to_move = ['h&p', 'h&p_interval', 'clinic_h&p_exam_and_progress_records', 'interval_h&p_note']

# Create a list of columns with the specified columns moved to the desired positions
new_columns_order = (
    export_df.columns[:2].tolist() +  # Columns before the insertion point
    columns_to_move +          # Columns to move
    [col for col in export_df.columns if col not in columns_to_move and col not in export_df.columns[:2]]  # Remaining columns
)

# Reorder the DataFrame columns
export_df = export_df[new_columns_order]

def df_to_txt(df):
    for i in range(df.shape[0]):
        txt = "#####################\n\n"    
        for j in range(df.shape[1]):
            if df.iloc[i,j] is not None:
                txt += df.columns[j] + ": " + str(df.iloc[i,j]) + "\n\n#####################\n\n"
        # export as .txt file
        with open(f'../exports/notes/export_df_{i+1}.docx', 'w') as f:
            f.write(txt)

df_to_txt(export_df)