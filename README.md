# Influencer Authenticity vs. AI-Generated Content
### Consumer Skepticism, Brand Credibility & Purchase Intention in the Age of Generative AI

A quantitative digital marketing research project examining how perceived influencer authenticity, AI content awareness, content transparency, and parasocial relationships are associated with consumer skepticism—and how skepticism relates to brand credibility and purchase intention.

**Main-study dataset:** 395 responses · 26 measurement items · 7 constructs

---

## Table of Contents
- [Project Overview](#project-overview)
- [Research Objectives](#research-objectives)
- [Conceptual Model](#conceptual-model)
- [Dataset and Constructs](#dataset-and-constructs)
- [Analysis Workflow](#analysis-workflow)
- [Key Findings](#key-findings)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Running the Analysis](#running-the-analysis)
- [Tools and Libraries](#tools-and-libraries)
- [Reproducibility and Data Privacy](#reproducibility-and-data-privacy)
- [Limitations](#limitations)
- [Research Team](#research-team)

---

## Project Overview

Influencer marketing depends partly on the trust audiences place in creators and their recommendations. Generative AI has made it easier to draft, edit, and produce influencer content, creating new questions about authenticity, disclosure, persuasion, and consumer trust.

This project investigates how four influencer- and content-related constructs relate to **Consumer Skepticism (CS)**, and how skepticism relates to two consumer outcomes: **Brand Credibility (BC)** and **Purchase Intention (PI)**. It also examines indirect relationships through consumer skepticism.

The project combines questionnaire-based research with a staged statistical analysis workflow. Python scripts are used for data preparation, descriptive analysis, reliability assessment, correlations, regression, mediation, diagnostics, demographic summaries, and predictive assessment.

## Research Objectives

1. Examine the relationships between Perceived Authenticity, AI Content Awareness, Content Transparency, Parasocial Relationship, and Consumer Skepticism.
2. Assess the relationships between Consumer Skepticism, Brand Credibility, and Purchase Intention.
3. Investigate indirect pathways from the four antecedent constructs to Brand Credibility and Purchase Intention through Consumer Skepticism.
4. Evaluate the quality, consistency, and predictive performance of the analyses.

## Conceptual Model

The research model contains four predictors of Consumer Skepticism. Consumer Skepticism is then linked to Brand Credibility and Purchase Intention.

```text
Perceived Authenticity ─┐
AI Content Awareness ───┤
Content Transparency ───┼──> Consumer Skepticism ───> Brand Credibility
Parasocial Relationship ┘                         └──> Purchase Intention
```

The model includes the following six direct hypotheses:

| Hypothesis | Proposed relationship | Expected direction |
|---|---|---|
| H1 | Perceived Authenticity → Consumer Skepticism | Negative |
| H2 | AI Content Awareness → Consumer Skepticism | Positive |
| H3 | Content Transparency → Consumer Skepticism | Negative |
| H4 | Parasocial Relationship → Consumer Skepticism | Negative |
| H5 | Consumer Skepticism → Brand Credibility | Negative |
| H6 | Consumer Skepticism → Purchase Intention | Negative |

Eight indirect pathways through Consumer Skepticism are also assessed: each of the four antecedents is linked indirectly to each of the two outcome constructs.

*These are statistical relationships in a cross-sectional study; they should not automatically be interpreted as causal effects.*

## Dataset and Constructs

The main-study analysis file contains **395 records** and **26 five-point Likert-scale measurement items** distributed across seven constructs.

| Code | Construct | Number of items | Model role |
|---|---|---:|---|
| PA | Perceived Authenticity | 4 | Predictor |
| ACA | AI Content Awareness | 4 | Predictor |
| CT | Content Transparency | 4 | Predictor |
| PSR | Parasocial Relationship | 4 | Predictor |
| CS | Consumer Skepticism | 4 | Intermediate / endogenous construct |
| BC | Brand Credibility | 3 | Outcome / endogenous construct |
| PI | Purchase Intention | 3 | Outcome / endogenous construct |
| **Total** | **7 constructs** | **26** | |

The item response scale ranges from **1 (Strongly Disagree) to 5 (Strongly Agree)**.

Raw respondent-level data are not intended to be committed to this public repository. Keep the source workbook and any potentially identifiable or sensitive data in approved local or access-controlled storage.

## Analysis Workflow

The scripts are organised as a staged workflow. The exact output files depend on the current project workspace and configured input paths.

### Stage 2 — Descriptive Statistics, Reliability, and Data Quality
- Item- and construct-level descriptive statistics
- Cronbach's alpha and corrected item–total statistics
- Normality testing and diagnostic plots
- Harman's single-factor screening test

### Stage 3 — Relationships Between Constructs
- Pearson correlation analysis
- Spearman rank-correlation analysis
- Regression models for Consumer Skepticism, Brand Credibility, and Purchase Intention
- Coefficients, significance tests, confidence intervals, and model-fit statistics

### Stage 4 — Mediation Analysis
- Indirect-effect estimation
- 5,000 bootstrap resamples
- Confidence intervals for indirect pathways
- Assessment of whether confidence intervals exclude zero

### Stage 5 — Missing-Data Checks and Regression Diagnostics
- Missing-data and model checks
- Mardia's multivariate normality statistics
- Studentized residuals and Cook's distance
- Residual Q–Q plots and residual-versus-fitted plots

### Stage 6 — Demographic Analysis
- Age and gender distributions
- Social-media usage and platform frequencies
- Screening and eligibility summaries
- Missing-response summaries

### Stage 7 — Item-Level Frequency Analysis
- Response frequencies for all 26 measurement items
- Percentages for Likert response options 1–5
- Item-level means, standard deviations, minimums, and maximums

### Stage 8 — Final Consistency Audit
- Expected questionnaire columns and input/output files
- Record counts and valid response ranges
- Construct-score coverage
- Item-frequency totals
- Regression-model and mediation-path coverage
- Programmed consistency checks

### Stage 9 — Predictive Assessment
- Ten-fold cross-validated prediction of endogenous-construct indicators
- Comparison of prediction errors against a mean-baseline model
- Summary statistics reported for Consumer Skepticism, Brand Credibility, and Purchase Intention

The Stage 9 output contains the project's predictive statistics. These values should be interpreted in line with the metric definition and validation design, and not assumed to be interchangeable with every PLS-SEM Q² implementation.

## Key Findings

The results available from the current analysis workflow show the following pattern:

- Perceived Authenticity, Content Transparency, and Parasocial Relationship are negatively associated with Consumer Skepticism.
- AI Content Awareness is positively associated with Consumer Skepticism.
- Consumer Skepticism is negatively associated with Brand Credibility and Purchase Intention.
- The eight specified indirect pathways through Consumer Skepticism were reported as statistically significant in the bootstrapped mediation analysis.

### Predictive statistics

| Endogenous construct | Predictors in the model | Q² / predictive statistic |
|---|---|---:|
| Consumer Skepticism (CS) | PA, ACA, CT, PSR | 0.111 |
| Brand Credibility (BC) | CS | 0.126 |
| Purchase Intention (PI) | CS | 0.092 |

All three reported values are positive. Brand Credibility has the highest reported value (0.126), followed by Consumer Skepticism (0.111) and Purchase Intention (0.092). These statistics should be reported with the correct metric label and interpreted alongside the broader model results.

## Repository Structure

The main analysis workspace includes the following scripts and outputs:

```text
Digital_Marketing_Project/
├── main_analysis.py
├── export_for_smartpls.py
├── stage2_analysis.py
├── stage3_relationships.py
├── stage4_mediation.py
├── stage5_missing_checks.py
├── stage6_demographic_analysis.py
├── stage6_find_demographics.py
├── stage7_item_frequencies.py
├── stage8_final_audit.py
├── stage9_predictive_assessment.py
├── requirements.txt
├── README.md
└── analysis_outputs/
    ├── main_study_numeric.xlsx          # local input; do not commit raw data
    ├── stage2_statistical_results.xlsx
    ├── stage3_relationship_results.xlsx
    ├── stage4_mediation_results.xlsx
    ├── stage5_missing_checks.xlsx
    ├── stage6_demographic_results.xlsx
    ├── stage7_item_frequency_results.xlsx
    ├── stage8_final_audit.xlsx
    ├── stage9_predictive_results.xlsx
    └── stage5_diagnostic_plots/
```

**Important:** This is a representative project layout. Local input workbooks and generated analysis files may not all be present in a fresh clone. Some scripts depend on local Excel files or intermediate outputs that are intentionally excluded from the public repository.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ArihantKhaitan/Digital_Marketing_Project.git
cd Digital_Marketing_Project
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the input data

Place the required numeric analysis workbook at the path expected by the scripts, or update the relevant input path in the script configuration. For the current analysis workflow, the expected workbook is:

```text
analysis_outputs/main_study_numeric.xlsx
```

This workbook is not guaranteed to be included in the public repository. Use only data you are permitted to access and process.

## Running the Analysis

Run the stages from the repository root in order. Some stages depend on outputs generated by earlier scripts.

```powershell
python stage2_analysis.py
python stage3_relationships.py
python stage4_mediation.py
python stage5_missing_checks.py
python stage6_demographic_analysis.py
python stage7_item_frequencies.py
python stage8_final_audit.py
python stage9_predictive_assessment.py
```

The output workbooks are written to `analysis_outputs/`, subject to each script's configured paths. `stage6_find_demographics.py` is an auxiliary script and may be used when checking or locating demographic fields.

**Reproducibility note:** A fresh clone may not run end-to-end until the required local input files are provided and paths are configured. Do not add raw survey data solely to make the repository runnable.

## Tools and Libraries

- **Python** — analysis scripting
- **Pandas and NumPy** — data manipulation and numerical computation
- **SciPy** — statistical tests
- **Statsmodels** — regression and statistical modelling
- **Scikit-learn** — cross-validation and predictive modelling
- **Matplotlib** — diagnostic and distribution plots
- **OpenPyXL** — Excel workbook read/write support
- **PLS-SEM workflow** — structural and measurement-model analysis as documented in the final project results

See [`requirements.txt`](requirements.txt) for the project's dependency list.

## Reproducibility and Data Privacy

- Do not commit respondent-level survey responses, contact details, or other identifying information.
- Do not commit passwords, access tokens, API keys, or other credentials.
- Check that aggregate outputs cannot expose individual responses before publishing them.
- Use consistent random seeds and document relevant analysis settings when repeatability matters.
- Keep a record of data-cleaning decisions, construct definitions, and changes to questionnaire items.
- Distinguish confirmatory hypothesis tests from exploratory or diagnostic analyses.
- A successful consistency audit means the programmed checks passed; it does not by itself establish representativeness, measurement validity, or correctness of every statistical assumption.

## Limitations

The study uses self-reported, cross-sectional survey data and a non-probability sampling approach. Findings may not generalise to all consumers or platforms. AI Content Awareness measures reported awareness or suspicion rather than objectively verified ability to identify AI-generated content. Statistical indirect effects from cross-sectional data should not be treated as conclusive causal mediation. Results should be considered alongside the quality of the measurement instrument, sampling process, and statistical assumptions.

## Research Team

**Arihant Khaitan** — [@ArihantKhaitan](https://github.com/ArihantKhaitan)  
**Ahamed Nazeer Haneefa**  
**Aqeel Abdul Khader**  
**Gaurav Raj**

**Project guide:** Dr. Ramnath Shenoy, Assistant Professor, Department of Humanities and Management, MIT Manipal.

---

*Under-Graduate Minor Project — Digital Marketing*  
*Influencer authenticity, AI-generated content awareness, consumer skepticism, brand credibility, and purchase intention.*
