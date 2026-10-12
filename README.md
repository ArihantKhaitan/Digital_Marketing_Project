# Influencer Authenticity vs. AI-Generated Content
### Main Study | Consumer Skepticism, Brand Credibility & Purchase Intention

A quantitative research project investigating how perceived influencer authenticity, AI content awareness, content transparency, and parasocial relationships relate to consumer skepticism, brand credibility, and purchase intention in influencer marketing.

**Study size:** 395 responses · 26 questionnaire items · 7 constructs

---

## Overview

Influencer marketing increasingly operates alongside AI-assisted content creation, sponsored posts, and digital creator–audience relationships. These developments raise questions about how consumers interpret influencer content and how their perceptions relate to trust in promoted brands and purchase decisions.

This project analyses survey responses to examine relationships between four influencer/content characteristics, consumer skepticism, and two consumer outcomes.

The analysis uses Python for statistical analysis and data-quality checks, with **SmartPLS 4 planned for the final PLS-SEM assessment**.

## Research Model

The study examines the following constructs:

| Code | Construct | Role in the research model |
|---|---|---|
| PA | Perceived Authenticity | Predictor |
| ACA | AI Content Awareness | Predictor |
| CT | Content Transparency | Predictor |
| PSR | Parasocial Relationship | Predictor |
| CS | Consumer Skepticism | Intermediate construct |
| BC | Brand Credibility | Outcome |
| PI | Purchase Intention | Outcome |

The proposed relationships examine whether PA, ACA, CT, and PSR are associated with CS, and whether CS is associated with BC and PI. The study also investigates indirect relationships through CS using bootstrapped mediation analysis.

*The conceptual relationships describe the study's proposed model; statistical associations do not, by themselves, establish causality.*

---

## Dataset

| Property | Description |
|---|---|
| Study type | Quantitative, questionnaire-based research |
| Main-study responses | 395 |
| Measurement items | 26 |
| Constructs | 7 |
| Response scale | Five-point Likert scale (1–5) |
| Analysis language | Python |
| Planned SEM software | SmartPLS 4 |

The analysis dataset contains four items each for PA, ACA, CT, PSR, and CS, and three items each for BC and PI.

The repository is intended to contain analysis code and aggregate outputs, **not raw respondent-level survey data**.

---

## Analysis Pipeline

### Stage 2 — Descriptive Statistics, Reliability & Data Quality

- Construct-level and item-level descriptive statistics
- Cronbach's alpha for internal consistency
- Corrected item–total correlations and alpha-if-item-deleted
- Normality tests and distribution plots
- Harman's single-factor test

### Stage 3 — Relationships Between Constructs

- Pearson correlation analysis
- Spearman rank-correlation analysis
- Multiple regression for Consumer Skepticism
- Regression models for Brand Credibility and Purchase Intention
- Regression coefficients, significance tests, confidence intervals, and model fit

### Stage 4 — Mediation Analysis

- Bootstrapped indirect-effect estimation
- 5,000 bootstrap resamples
- Confidence intervals for indirect effects
- Assessment of whether each interval includes zero

### Stage 5 — Regression Diagnostics

- Multivariate normality assessment using Mardia's statistics
- Studentized residuals
- Cook's distance
- Residual Q–Q plots
- Residuals-versus-fitted plots

### Stage 6 — Demographic Analysis

- Age and gender distributions
- Social media usage frequency
- Platform usage frequencies
- Eligibility and screening summaries
- Missing-response summaries

### Stage 7 — Item-Level Frequency Analysis

- Frequency of each Likert response (1–5) for all 26 items
- Percentage distributions
- Item-level means, standard deviations, minimums, and maximums

### Stage 8 — Final Consistency Audit

- Expected files and questionnaire columns
- Response counts and value ranges
- Construct-score coverage
- Item-frequency totals
- Regression model and mediation-path coverage
- Output validation checks

### Final Stage — PLS-SEM in SmartPLS 4

The planned PLS-SEM stage includes measurement-model assessment, structural-model evaluation, and bootstrap significance testing. This stage remains separate from the completed Python consistency checks.

---

## Project Structure

```text
Main-Study/
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
├── requirements.txt
├── README.md
└── analysis_outputs/
    ├── stage2_summary_for_sharing.xlsx
    ├── stage3_relationship_results.xlsx
    ├── stage4_mediation_results.xlsx
    ├── stage5_missing_checks.xlsx
    ├── stage6_demographic_results.xlsx
    ├── stage7_item_frequency_results.xlsx
    ├── stage8_final_audit.xlsx
    └── stage5_diagnostic_plots/
```

The exact contents of `analysis_outputs/` may vary as analyses are updated. Files containing respondent-level data are intentionally excluded.

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ArihantKhaitan/Digital_Marketing_Project.git
cd Digital_Marketing_Project
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the analysis scripts

Run each stage from the project root, after ensuring the required input files are available in your approved local research-data directory.

```bash
python stage2_analysis.py
python stage3_relationships.py
python stage4_mediation.py
python stage5_missing_checks.py
python stage6_demographic_analysis.py
python stage7_item_frequencies.py
python stage8_final_audit.py
```

**Note:** Some scripts require the original survey or intermediate workbooks, which are not included in this repository. The scripts may therefore require locally configured input paths before they can be reproduced from a fresh clone.

---

## Tools & Technologies

- **Python** — statistical analysis and automation
- **Pandas & NumPy** — data processing and numerical analysis
- **SciPy** — statistical tests
- **Statsmodels & Scikit-learn** — regression and supporting statistical procedures
- **Matplotlib** — distribution and diagnostic visualisations
- **OpenPyXL** — Excel workbook processing
- **SmartPLS 4** — planned PLS-SEM measurement and structural model assessment

---

## Reproducibility & Data Privacy

- Respondent-level survey data should remain in approved, access-controlled storage.
- Do not commit raw survey exports, identifiable information, credentials, or private research files.
- Aggregate results should be checked before publication to ensure they cannot expose individual responses.
- Bootstrap results can vary slightly between runs unless random seeds and implementation settings are fixed.
- Statistical findings should be interpreted in line with the study design, measurement quality, and stated hypotheses.

## Research Status

The Python analysis scripts have generated the preliminary statistical outputs, and the programmed consistency audit passed its checks. The final SmartPLS 4 measurement- and structural-model assessment is a separate remaining step.

## Author

**Arihant Khaitan**  
GitHub: [@ArihantKhaitan](https://github.com/ArihantKhaitan)

---

*Academic research project on influencer marketing, AI-generated content awareness, consumer skepticism, brand credibility, and purchase intention.*