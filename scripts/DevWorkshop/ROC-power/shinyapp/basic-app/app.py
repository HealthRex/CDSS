# conda activate shiny_env
from shiny import App, render, ui, reactive
from numpy import random
from three_panel import *

app_ui = ui.page_fluid(ui.panel_title("Sample Size for Comparing Models' Area Under the ROC Curve:", "Sample Size for Comparing AUROCs"),  
    ui.h4("Specifying parameters of two joint distributions"),
    ui.br(),
    ui.h4("- Inputs"),
    "In the absence of a pilot test set, you need to manually specify a distribution for the evaluation population (illustrated in real-time in the contour plots below.)",
    ui.p("Once this distribution is specified, use ", ui.em("Run the simulations.")), 
    ui.row(
        ui.column(
            4,
            ui.strong("For cases (event occurs)"),
            ui.input_slider("X_mean1", ui.p("Mean parameter for model A", ui.br(), ui.em("How well will model A do on cases?")), value=.42, step=.01, min=1e-2, max=1-1e-2),
            ui.input_slider("Y_mean1", ui.p("Mean parameter for model B", ui.br(), ui.em("How well will model B do on cases?")), value=.37, step=.01, min=1e-2, max=1-1e-2),
            ui.input_switch("change_var1", "Change variance parameters for cases", False, width='375px'),
            ui.output_ui("ui_X_var1"),
            ui.output_ui("ui_Y_var1"),
            ui.input_switch("change_cor1", "Change correlation parameter for cases", False, width='375px'),
            ui.output_ui("ui_corr1"),
            ui.output_ui("ui_spacing"), 
            ui.output_plot("hist", width='850px', height='850px'),
        ),
        ui.column(
            4,
            ui.strong("For controls (event does not occur)"),
            ui.input_slider("X_mean2", ui.p("Mean parameter for model A", ui.br(), ui.em("How well will model A do on controls?")), value=.9, step=.01, min=1e-2, max=1-1e-2),
            ui.input_slider("Y_mean2", ui.p("Mean parameter for model B", ui.br(), ui.em("How well will model B do on controls?")), value=.9, step=.01, min=1e-2, max=1-1e-2),
            ui.input_switch("change_var2", "Change variance parameters for controls", False, width='375px'),
            ui.output_ui("ui_X_var2"),
            ui.output_ui("ui_Y_var2"),
            ui.input_switch("change_cor2", "Change correlation parameter for controls", False, width='375px'),
            ui.output_ui("ui_corr2"),
        ),
        ui.column(4,
            ui.strong("Simulation"),
            ui.input_slider("prev", ui.p("Prevalence in the evaluation population", ui.br(), ui.em("What is the anticipated proportion of events in the test set?")), value=.2, step=.01, min=1e-2, max=1-1e-2),
            ui.input_slider("alpha_t", ui.p("Alpha threshold", ui.br(), ui.em("Significance level, typically set to 0.05")), value=.05, step=.01, min=1e-2, max=1-1e-2),
            ui.input_numeric("ss", ui.p("Sample size for power calculation", ui.br(), ui.em("Calculations are also performed at 0.5 and 1.5 that sample size")), value=770, min=100, max=100000),
            ui.input_select("n_sim", ui.p(ui.strong(ui.div({"style": "font-weight: bold; color: red;"}, "Run the simulations")), ui.em("Choose no. of iterations")), choices={0: "No iteration (for parameter selection)", 100: "100 iterations (fastest, least accurate)", 500: "500 iterations (intermediate)", 2000: "2000 iterations (slowest, most accurate)"}),
        )
    ),
    ui.br(),
    ui.output_ui("ui_text_meth"),
)

def server(input, output, session):
    
    @output
    @render.plot
    def hist():
           return three_panel(X_mean1=input.X_mean1(), Y_mean1=input.Y_mean1(), X_var1=input.X_var1() if input.change_var1() else .9, Y_var1=input.Y_var1() if input.change_var1() else .9, corr1=input.corr1() if input.change_cor1() else .9,
                           X_mean2=1-input.X_mean2(), Y_mean2=1-input.Y_mean2(), X_var2=input.X_var2() if input.change_var2() else .9, Y_var2=input.Y_var2() if input.change_var2() else .9, corr2=input.corr2() if input.change_cor2() else .9,
                           ss=input.ss(), prev=input.prev(), alpha_t=input.alpha_t(), n_sim=None if int(input.n_sim()) == 0 else int(input.n_sim())) 
        
    @render.ui 
    @reactive.event(input.change_var1)
    def ui_X_var1(): 
        if input.change_var1():
            value = input.X_var1() if "X_var1" in input else .9
            return ui.input_slider("X_var1", ui.p("Variance parameter for model A", ui.br(), ui.em("How variable will model A be on cases?")), value=.9, step=.01, min=1e-2, max=1-1e-2)
        
    @render.ui 
    @reactive.event(input.change_var1)
    def ui_Y_var1(): 
        if input.change_var1():
            value = input.Y_var1() if "Y_var1" in input else .9
            return ui.input_slider("Y_var1", ui.p("Variance parameter for model B", ui.br(), ui.em("How variable will model B be on cases?")), value=.9, step=.01, min=1e-2, max=1-1e-2)
    
    @render.ui 
    @reactive.event(input.change_cor1)
    def ui_corr1(): 
        if input.change_cor1():
            value = input.corr1() if "corr1" in input else .9
            return ui.input_slider("corr1", ui.p("Correlation parameter for models A & B", ui.br(), ui.em("How close will predictions be on cases?")), value=.9, step=.01, min=0, max=1-1e-2)
        
    @render.ui 
    @reactive.event(input.change_var2)
    def ui_X_var2(): 
        if input.change_var2():
            value = input.X_var2() if "X_var2" in input else .9
            return ui.input_slider("X_var2", ui.p("Variance parameter for model A", ui.br(), ui.em("How variable will model A be on controls?")), value=.9, step=.01, min=1e-2, max=1-1e-2)
        
    @render.ui 
    @reactive.event(input.change_var2)
    def ui_Y_var2(): 
        if input.change_var2():
            value = input.Y_var2() if "Y_var2" in input else .9
            return ui.input_slider("Y_var2", ui.p("Variance parameter for model B", ui.br(), ui.em("How variable will model B be on controls?")), value=.9, step=.01, min=1e-2, max=1-1e-2)
    
    @render.ui 
    @reactive.event(input.change_cor2)
    def ui_corr2(): 
        if input.change_cor2():
            value = input.corr1() if "corr2" in input else .9
            return ui.input_slider("corr2", ui.p("Correlation parameter for models A & B", ui.br(), ui.em("How close will predictions be on controls?")), value=.9, step=.01, min=0, max=1-1e-2)
    
    @render.ui
    @reactive.event(input.n_sim)
    def ui_text_meth(): 
        if int(input.n_sim()) == 0:
            return 
        else:
           return ui.h4("- Methods"), "In the plot above, each dot represents a DeLong p-value calculated on a dataset of the corresponding sample size. Each dataset is obtained by sampling from the specified probability distribution. Power is estimated as the fraction of p-values below the significance level."

    @render.ui
    @reactive.event(input.change_var1, input.change_cor1, input.change_var2, input.change_cor2)
    def ui_spacing():
        if input.change_var2() and not input.change_cor2() and not input.change_var1():
            if input.change_cor1():
                return ui.div({"style": "margin-bottom: 140px;"}), ui.h4("- Results")
            else:
                return ui.div({"style": "margin-bottom: 275px;"}), ui.h4("- Results")
        elif input.change_cor2() and not input.change_var2() and not input.change_var1() and not input.change_cor1():
            return ui.div({"style": "margin-bottom: 140px;"}), ui.h4("- Results")
        elif input.change_var2() and input.change_cor2() and not (input.change_var1() and input.change_cor1()):
            if input.change_cor1():
                return ui.div({"style": "margin-bottom: 270px;"}), ui.h4("- Results")
            elif input.change_var1():
                return ui.div({"style": "margin-bottom: 135px;"}), ui.h4("- Results")
            else:
                return ui.div({"style": "margin-bottom: 400px;"}), ui.h4("- Results")
        else:
            return ui.h4("- Results")
    
app = App(app_ui, server)