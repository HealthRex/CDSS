# conda activate shiny_env
from shiny import App, render, ui, reactive
from numpy import random
from three_panel import *

app_ui = ui.page_fixed(ui.panel_title("Sample Size for Comparing Models' Area Under the ROC Curve:", "Sample Size for Comparing AUROCs"),  
    ui.h4("Specifying parameters of two joint distributions"), 
    ui.row(
        ui.column(
            4,
            "For cases (event occurs):",
            ui.input_slider("X_mean1", label="- Model A: Mean parameter", value=.7, step=.01, min=1e-2, max=1-1e-2),
            ui.input_slider("Y_mean1", label="- Model B: Mean parameter", value=.6, step=.01, min=1e-2, max=1-1e-2),
            ui.input_switch("change_var1", "Change variance parameters", False),
            ui.output_ui("ui_X_var1"),
            ui.output_ui("ui_Y_var1"),
            ui.input_switch("change_cor1", "Change correlation parameter", False),
            ui.output_ui("ui_corr1"),
        ),
        ui.column(
            4,
            "For controls (event does not occur):",
            ui.input_slider("X_mean2", label="- Model A: Mean parameter", value=.3, step=.01, min=1e-2, max=1-1e-2),
            ui.input_slider("Y_mean2", label="- Model B: Mean parameter", value=.4, step=.01, min=1e-2, max=1-1e-2),
            ui.input_switch("change_var2", "Change variance parameters", False),
            ui.output_ui("ui_X_var2"),
            ui.output_ui("ui_Y_var2"),
            ui.input_switch("change_cor2", "Change correlation parameter", False),
            ui.output_ui("ui_corr2"),
        ),
        ui.column(2,
            "Simulation:",
            ui.input_numeric("ss", label="- Sample Size", value=260, min=100, max=100000),
            ui.input_slider("prev", label="- Prevalence", value=.1, step=.01, min=1e-2, max=1-1e-2),
            ui.input_slider("alpha_t", label="- Alpha threshold", value=.05, step=.01, min=1e-2, max=1-1e-2),
            ui.input_select("n_sim", label=ui.markdown("**Choose no. of iterations to run the simulations**"), choices={0: "Zero (for parameter selection)", 100: "100 simulations (fastest, least accurate)", 500: "500 simulations (intermediate)", 2000: "2000 simulations (slowest, most accurate)"}),
        )
    ),
    ui.row(
        ui.column(5, ui.output_plot("hist", width='1000px', height='1000px'),)
    ),
)

def server(input, output, session):
    
    @output
    @render.plot
    def hist():
           return three_panel(X_mean1=input.X_mean1(), Y_mean1=input.Y_mean1(), X_var1=input.X_var1() if input.change_var1() else .9, Y_var1=input.Y_var1() if input.change_var1() else .9, corr1=input.corr1() if input.change_cor1() else .6,
                           X_mean2=input.X_mean2(), Y_mean2=input.Y_mean2(), X_var2=input.X_var2() if input.change_var2() else .9, Y_var2=input.Y_var2() if input.change_var2() else .9, corr2=input.corr2() if input.change_cor2() else .6,
                           ss=input.ss(), prev=input.prev(), alpha_t=input.alpha_t(), n_sim=None if int(input.n_sim()) == 0 else int(input.n_sim())) 
        
    @render.ui 
    @reactive.event(input.change_var1)
    def ui_X_var1(): 
        if input.change_var1():
            value = input.X_var1() if "X_var1" in input else .9
            return ui.input_slider("X_var1", "- Model A: Variance parameter", value=.9, step=.01, min=1e-2, max=1-1e-2)
        
    @render.ui 
    @reactive.event(input.change_var1)
    def ui_Y_var1(): 
        if input.change_var1():
            value = input.Y_var1() if "Y_var1" in input else .9
            return ui.input_slider("Y_var1", "- Model B: Variance parameter", value=.9, step=.01, min=1e-2, max=1-1e-2)
    
    @render.ui 
    @reactive.event(input.change_cor1)
    def ui_corr1(): 
        if input.change_cor1():
            value = input.corr1() if "corr1" in input else .6
            return ui.input_slider("corr1", "- Correlation between models A and B", value=.6, step=.01, min=0, max=1-1e-2)
        
    @render.ui 
    @reactive.event(input.change_var2)
    def ui_X_var2(): 
        if input.change_var2():
            value = input.X_var2() if "X_var2" in input else .9
            return ui.input_slider("X_var2", "- Model A: Variance parameter", value=.9, step=.01, min=1e-2, max=1-1e-2)
        
    @render.ui 
    @reactive.event(input.change_var2)
    def ui_Y_var2(): 
        if input.change_var2():
            value = input.Y_var2() if "Y_var2" in input else .9
            return ui.input_slider("Y_var2", "- Model B: Variance parameter", value=.9, step=.01, min=1e-2, max=1-1e-2)
    
    @render.ui 
    @reactive.event(input.change_cor2)
    def ui_corr2(): 
        if input.change_cor2():
            value = input.corr1() if "corr2" in input else .6
            return ui.input_slider("corr2", "- Correlation between models A and B", value=.6, step=.01, min=0, max=1-1e-2)

app = App(app_ui, server)