from shiny import App, render, ui
from scipy.stats import norm
from stat_custom import collins_c

app_ui = ui.page_fluid(
    ui.panel_title("Sample Size Needed to Precisely Estimate a Model's Area Under the ROC Curve"),
    ui.br(),
    ui.input_slider("auroc", label="Anticipated true AUROC", value=.77, step=.01, min=.5, max=1-1e-2),
    ui.input_slider("prev", label="Prevalence", value=.43, step=.01, min=1e-2, max=1-1e-2),
    ui.input_numeric("targ_se", "Target standard error", value=.0255, step=.0001, min=1e-2, max=1-1e-2),
    ui.br(),
    ui.output_text("txt1"),
    ui.div(
    {"style": "font-weight: bold; text-indent: 40px;"},
    ui.output_text("txt2"),
    ),
    ui.br(),
    "References:",
    ui.br(),
    "- Riley et al. Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study. BMJ (2024) [",
    ui.a("link", href="https://www.bmj.com/content/384/bmj-2023-074821", target="_blank"), "].",
    ui.br(),
    "- Newcombe. Confidence intervals for an effect size measure based on the Mann-Whitney statistic. Part 2: asymptotic methods and evaluation. Statistics in medicine (2006) [",
    ui.a("link", href="https://onlinelibrary.wiley.com/doi/10.1002/sim.2324", target="_blank"), "]."
)

def server(input, output, session):
    @output
    @render.text
    def txt1():
        ins = collins_c(c=input.auroc(), p=input.prev(), targ_se = input.targ_se())
        req_N = ins.cal_N_loop()
        return f"To achieve a 95% confidence interval for the AUROC that is less than {norm.ppf(0.975)*2*input.targ_se():.2f} in width,"
    
    @output
    @render.text
    def txt2():
        ins = collins_c(c=input.auroc(), p=input.prev(), targ_se = input.targ_se())
        req_N = ins.cal_N_loop()
        return f"a minimum sample size of {req_N} is needed ({int(req_N*input.prev())} events.)"

app = App(app_ui, server)