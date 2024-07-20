# This app is translated from Mastering Shinywidgets
# https://mastering-shiny.org/basic-reactivity.html#reactive-expressions-1
from shiny import App, render, ui, reactive
from numpy import random
import asyncio
from three_panel import *

app_ui = ui.page_fixed(   
    ui.row(
        ui.column(
            4,
            "For cases (event occurs)",
            ui.input_slider("X_mean1", label="Model A: Mean parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("X_var1", label="Model A: Variance parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("Y_mean1", label="Model B: Mean parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("Y_var1", label="Model B: Variance parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("corr1", label="Correlation between models A and B", value=.2, min=1e-3, max=1-1e-3),
        ),
        ui.column(
            4,
            "For controls (event does not occur)",
            ui.input_slider("X_mean2", label="Model A: Mean parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("X_var2", label="Model A: Variance parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("Y_mean2", label="Model B: Mean parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("Y_var2", label="Model B: Variance parameter", value=.2, min=1e-3, max=1-1e-3),
            ui.input_slider("corr2", label="Correlation between models A and B", value=.2, min=1e-3, max=1-1e-3),
        ),
        ui.column(2,
            "Simulation",
            ui.input_numeric("ss", label="Sample Size", value=500, min=100, max=100000),
            ui.input_slider("prev", label="Prevalence", value=.05, min=1e-3, max=1-1e-3),
            ui.input_slider("alpha_t", label="Alpha threshold", value=.05, min=1e-3, max=1-1e-3),
            ui.input_select("n_sim", label=ui.markdown("**Choose no. of iterations to run the simulations**"), choices={0: "Zero (no simulation)", 500: 500, 1000: 1000, 2000: 2000}),
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
        return three_panel(X_mean1=input.X_mean1(), Y_mean1=input.Y_mean1(), X_var1=input.X_var1(), Y_var1=input.Y_var1(), corr1=input.corr1(),
                           X_mean2=input.X_mean2(), Y_mean2=input.Y_mean2(), X_var2=input.X_var2(), Y_var2=input.Y_var2(), corr2=input.corr2(),
                           ss=input.ss(), prev=input.prev(), alpha_t=input.alpha_t(), n_sim=None if int(input.n_sim()) == 0 else int(input.n_sim()))

app = App(app_ui, server)