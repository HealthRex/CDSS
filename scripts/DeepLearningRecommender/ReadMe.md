## ClinicNet and ClinicLSTM Deep Learning Recommender Engine
*Authors: Delaney Sullivan, Jonathan Wang, Alex Wells, Adam Wells*

Hello, welcome to the HealthRex DeepLearning Recommender Github Folder!

Here you can find the files we use for automated patient progression prediction and clinical decision support through deep neural networks.

---
* ClinicNet is our FeedForward Model 	
* ClinicLSTM is our RNN model (may need load_and_format_data, rnn_data_wrapper, and create_batches files to preprocess data) 	
* human_authored_baseline allows one to compare results directly to the performance of human authored order sets.	
* makeMatrix is the code used for data preprocessing (which relies on FeatureMatrix.py and FeatureMatrixFactory.py, which was code originally writte by Santosh but further modified by us for our needs. Our modifications are located in this folder.)
---

The remainder of the code used to extract our data is located in the analysis folder.

Published Work and Suggested Reference: 
