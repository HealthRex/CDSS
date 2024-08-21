# rsconnect deploy shiny shinyapp/collins --name francois-grolleau --title prec_auroc1
# rsconnect deploy shiny shinyapp/pilot --name francois-grolleau --title ss_auroc_pilot
# rsconnect deploy shiny shinyapp/basic-app --name francois-grolleau --title ss_auroc

from shiny import App, render, ui
from scipy.stats import norm
from stat_custom import collins_c

app_ui = ui.page_fluid(
    ui.panel_title("Sample Size Needed to Precisely Estimate a Model's Area Under the ROC Curve"),
    ui.br(),
    ui.h4("- Inputs"),
    ui.input_slider("auroc", label=ui.p(ui.strong(ui.div({"style": ""},"Anticipated AUROC in the evaluation population")), ui.em("How well do we expect the model to perform on the test set?")), value=.77, step=.01, min=.5, max=1-1e-2, width="600px"),
    ui.input_slider("prev", label=ui.p(ui.strong(ui.div({"style": ""},"Prevalence in the evaluation population")), ui.em("What is the anticipated proportion of events in the test set?")), value=.43, step=.01, min=1e-2, max=1-1e-2, width="600px"),
    ui.input_numeric("targ_ciw", label=ui.p(ui.strong(ui.div({"style": ""},"Target width for the estimated AUROC 95% confidence interval")), ui.em("What level of precision do we aim to achieve for model evaluation?")), value=.1, step=.0001, min=1e-2, max=1-1e-2, width="600px"),
    ui.br(),
    ui.h4("- Result"),
    ui.div(
    {"style": "font-weight: bold; text-indent: 40px; font-size: 18px;"},
    ui.output_text("txt2"),
    ),
    ui.output_text("txt1"),
    ui.br(),
    ui.h4("- Methods"),
    "Our code uses an iterative process over the equation given in the references below to identify the sample size needed to achieve the desired precision for the AUROC estimate.",
    ui.div({"style": "margin-bottom: 20px;"}),
    "References:",
    ui.br(),
    "- Riley et al. Evaluation of clinical prediction models (part 3): calculating the sample size required for an external validation study. BMJ (2024) [See Figure 3, Criterion 3, ",
    ui.a("link", href="https://www.bmj.com/content/384/bmj-2023-074821", target="_blank"), "].",
    ui.br(),
    "- Newcombe. Confidence intervals for an effect size measure based on the Mann-Whitney statistic. Part 2: asymptotic methods and evaluation. Statistics in medicine (2006) [See V2 formula, Section 2.2, ",
    ui.a("link", href="https://onlinelibrary.wiley.com/doi/10.1002/sim.2324", target="_blank"), "]."
)

def server(input, output, session):
    @output
    @render.text
    def txt1():
        return f"to achieve a 95% confidence interval for the AUROC that is less than {input.targ_ciw()} in width, assuming a true AUROC of {input.auroc()} and a prevalence of {input.prev()*100:.0f}%."
    
    @output
    @render.text
    def txt2():
        ins = collins_c(c=input.auroc(), p=input.prev(), targ_se = input.targ_ciw()/(2*norm.ppf(0.975)))
        req_N = ins.cal_N_loop()
        return f"A minimum sample size of {req_N} ({int(req_N*input.prev())} events) is needed"

app = App(app_ui, server)