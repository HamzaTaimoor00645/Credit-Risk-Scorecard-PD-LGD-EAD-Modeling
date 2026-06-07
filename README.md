# Credit Risk Scorecard & Expected Loss Modeling

An end-to-end credit risk modeling project that develops a credit scorecard using Logistic Regression and XGBoost, estimates Probability of Default (PD), Loss Given Default (LGD), Exposure at Default (EAD), and calculates Expected Loss (EL).

## Features

* Data preprocessing and feature engineering
* Weight of Evidence (WoE) transformation
* Information Value (IV) analysis
* Logistic Regression scorecard model
* XGBoost challenger model
* Model evaluation using AUC, Gini, and KS
* PD, LGD, and EAD estimation
* Expected Loss calculation
* Stress testing scenarios
* Interactive Streamlit dashboard

## Tech Stack

* Python
* Pandas
* NumPy
* Scikit-Learn
* XGBoost
* Plotly
* Streamlit

## Expected Loss Formula

```text
Expected Loss = PD × LGD × EAD
```
Where:

* PD = Probability of Default
* LGD = Loss Given Default
* EAD = Exposure at Default


## Key Outcomes

* Built an interpretable credit scorecard for risk assessment
* Compared traditional and machine learning approaches
* Estimated portfolio-level expected losses
* Performed stress testing under adverse scenarios
* Created an interactive dashboard for risk monitoring

