import pandas as pd
from three_panel_pilot import *
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo

app_ui = ui.page_fluid(ui.panel_title("Sample Size for Comparing Models' Area Under the ROC Curve:", "Sample Size for Comparing AUROCs"),
    ui.h4("Using a pilot test set"),
    ui.br(),
    ui.h4("- Inputs"),
    ui.input_file("file1", "Please upload a pilot test set as a CSV file", accept=[".csv"], multiple=False, button_label='Upload .CSV file', width='400px'),
    ui.output_text("text"),
    ui.output_table("summary_csv"),
    ui.input_switch("change_prev", "Vary the prevalence from the pilot test set", False, width='400px'),
    ui.output_text("ui_text_prev"),
    ui.output_ui("ui_prev"),
    ui.br(),
    ui.row(
    ui.input_slider("alpha_t", label=ui.p("Alpha threshold", ui.br(), ui.em("Significance level, typically set to 0.05")), value=.05, step=.01, min=1e-2, max=1-1e-2, width='300px'),
    ui.input_numeric("ss", label=ui.p("Sample size for power calculation", ui.br(), ui.em("Calculations are also performed at 0.5 and 1.5 that sample size")), value=1060, min=100, max=100000, width='475px'),
    ui.input_select("n_sim", label=ui.p(ui.strong("Run the simulations"), ui.br(), ui.em("Choose no. of iterations")), choices={100: "100 iteration (fastest, least accurate)", 500: "500 iterations (intermediate)", 2000: "2000 iterations (slowest, most accurate)"}),
),  
    ui.br(),
    ui.h4("- Results"),
    ui.row(ui.output_plot("int_plot", width='1000px', height='750px'),),
    "In the plot above, each dot represents a DeLong p-value calculated on a dataset of the corresponding sample size. Each dataset is obtained by resampling with replacement from the pilot test set. If the prevalence is varied, the pilot test set is reweighed accordingly before resampling."
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def text():
        df = parsed_file()
        if getattr(df, "orig", False):
            return "Your CSV file should follow the column order as illustrated in the example: Event, Prediction from Model A, Prediction from Model B. Note that the specific column names are not required, only the order matters. For accurate sample size calculations, we recommend including a minimum of five events and five non-events in your dataset.  Before you upload your CSV file, we will use the example dataset below to demonstrate sample size calculation. Upon upload, the first ten rows of your pilot test will be shown for sanity checks."
        return "The first 10 rows of your uploaded test set are displayed below."

    @reactive.calc
    def parsed_file():
        file: list[FileInfo] | None = input.file1()
        if file is None:
            df = pd.read_csv("pilot.csv")
            df.orig = True
            df['Event'] = df['Event'].astype(int)
            return df
        return pd.read_csv(file[0]["datapath"])

    @render.table
    def summary_csv():
        df = parsed_file()
        def_cols = ["Event", "Prediction from model A", "Prediction from model B"]
        return df.iloc[:10, :3].rename(columns={col: def_cols[i] for i, col in enumerate(df.columns) if i < 3})
    
    @render.text
    @reactive.event(input.change_prev)
    def ui_text_prev(): 
        if input.change_prev():
            return "Anticipated prevalence in the evaluation population. If you are unsure, we recommend not to vary the prevalence."
    
    @render.ui 
    @reactive.event(input.change_prev)
    def ui_prev(): 
        if input.change_prev():
            value = input.prev() if "prev" in input else .5
            return ui.input_slider("prev", ui.em('What is the anticipated proportion of events in the final test set?'), value=.5, step=.01, min=1e-2, max=1-1e-2, width="600px")

    @output
    @render.plot
    def int_plot():
        return three_panel_pilot(parsed_file(), ss=input.ss(), alpha_t=input.alpha_t(), n_sim=int(input.n_sim()), change_prev=input.change_prev(), prev= input.prev() if input.change_prev() else None)

app = App(app_ui, server)