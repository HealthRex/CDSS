# LNPP Report Reproduction Steps

## How to generate data and analyses

`python scripts/LabTestAnalysis/machine_learning/LabNormalityPredictionPipeline`

This command will (1) build feature matrices if they do not already
exist, (2) build models if they do not already exist, and (3) analyze those
models.

If you don't want to regenerate all data from scratch (takes ~1-2 hours to
build feature matrices and all models for a single lab), just fetch the
data from Box: https://stanfordmedicine.app.box.com/folder/48741904687

In particular, download folder to
`scripts/LabTestAnalysis/machine_learning/data`, such that the folder contains
`scripts/LabTestAnalysis/machine_learning/data/LAB*`.

## How to generate report figures

Once all the data files are generated, run
`python scripts/LabTestAnalysis/report/LabNormalityReport.py`.

After ~1 minute of execution, it will have generated the following files in
whatever directory was used to invoke the script:
* algorithm-performance-summary.tab
* predictable-labs.tab (Table 1)
* predictable-and-expensive-charges.[eps/png] (Figure 3)

Figures 1 and 2 (flowcharts) were edited in Figma. For access, use log in with
Google from stanford.healthrex@gmail.com
https://www.figma.com/file/ES38bkPcFoSCEziZrkgBRh3u/LNPP

The remainder of the the tables were hand-generated in Google Sheets.
https://docs.google.com/document/d/1qoFkphFuJ0CzhubSRXSWPk7WJQoSY43oFAAThJe91tc/edit
* Table 2: decision-processes tab
* Table A1: feature-summary tab
* Table A2: algorithm-summary tab
