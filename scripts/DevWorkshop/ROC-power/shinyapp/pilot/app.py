import pandas as pd
from shinyapp.pilot.three_panel_pilot import *
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo

app_ui = ui.page_fluid(
    ui.input_file("file1", "Choose CSV File", accept=[".csv"], multiple=False),
    ui.output_text("text"),
    ui.output_table("summary_csv"),
    ui.input_switch("show_slider", "Change prevalence", True),
    ui.output_ui("ui_slider"),
    ui.row(
    ui.input_numeric("ss", label="Sample Size", value=830, min=100, max=100000),
    ui.input_slider("alpha_t", label="Alpha threshold", value=.05, min=1e-3, max=1-1e-3),
    ui.input_select("n_sim", label=ui.markdown("**Choose no. of iterations to run the simulations**"), choices={100: "100 simulations (fastest)", 500: "500 simulations (intermediate)", 2000: "2000 simulations (slowest)"}),
),
    ui.row(ui.output_plot("int_plot", width='1000px', height='750px'),),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def text():
        df = parsed_file()
        if getattr(df, "orig", False):
            return "Please upload a pilot test set as a CSV file formated as below:"
        return "The first 10 rows of your uploaded test set are displayed below."

    @reactive.calc
    def parsed_file():
        file: list[FileInfo] | None = input.file1()
        if file is None:
            df = pd.read_csv("shinyapp/pilot/pilot.csv")
            df.orig = True
            return df
        return pd.read_csv(file[0]["datapath"])

    @render.table
    def summary_csv():
        df = parsed_file()
        def_cols = ['Y', 'Y_hat_A', 'Y_hat_B']
        return df.iloc[:10, :3].rename(columns={col: def_cols[i] for i, col in enumerate(df.columns) if i < 3})
    
    @render.ui  # <<
    @reactive.event(input.show_slider)  # <<
    def ui_slider():  # <<
        if input.show_slider():
            value = input.slider() if "slider" in input else .5
            return ui.input_slider("slider", "Prevalence", value=value, min=1e-3, max=1-1e-3)
            

    @output
    @render.plot
    def int_plot():
        return three_panel_pilot(parsed_file(), ss=input.ss(), alpha_t=input.alpha_t(), n_sim=int(input.n_sim()))

app = App(app_ui, server)