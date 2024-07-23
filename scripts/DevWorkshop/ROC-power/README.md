# Model ROC power
 
<!-- badges: start -->
[![Python 3.12.3](https://img.shields.io/badge/Python-3.12.3-blue.svg)](https://www.Python.org) 
[![R 4.3.3](https://img.shields.io/badge/R-4.3.3-blue.svg)](https://www.r-project.org) 
<!-- badges: end -->

This repository provides short tutorials for the development and evaluation of clinical prediction models.

### Tutorials

 `roc_power.ipynb` Compare the discrimination of two trained models. Run simulations to calculate the power of your tests.

 `fit_models.ipynb` Train a Random Forrest and a Neural Network on synthetic data

 `data_gen.ipynb` Generate clinical data non parametrically

 ### Power to Detect Differences in Discrimintion: P3D app

To run your own simulations for power calculation, launch the P3D app by using the following commands in the terminal:

- `cd path/to/P3D`
- `pip install voila`
- `voila P3D.ipynb`

 ### Authors
This repository is written and maintained by François Grolleau (grolleau@stanford.edu).