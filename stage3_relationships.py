
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "analysis_outputs" / "stage2_statistical_results.xlsx"
OUT_DIR = BASE_DIR / "analysis_outputs"

scores = pd.read_excel(
    INPUT_FILE, sheet_name="Construct_Scores"
)

constructs = ["PA", "ACA", "CT", "PSR", "CS", "BC", "PI"]

if scores[constructs].isna().any().any():
    raise ValueError("Missing construct scores found.")

# --------------------------------------------------
# 1. CORRELATION ANALYSIS
# --------------------------------------------------

pearson = scores[constructs].corr(method="pearson")
spearman = scores[constructs].corr(method="spearman")

def correlation_pvalues(data, method):
    cols = data.columns
    pvals = pd.DataFrame(
        np.eye(len(cols)), index=cols, columns=cols
    )

    for i, a in enumerate(cols):
        for j in range(i + 1, len(cols)):
            b = cols[j]

            if method == "pearson":
                _, p = stats.pearsonr(data[a], data[b])
            else:
                _, p = stats.spearmanr(data[a], data[b])

            pvals.loc[a, b] = p
            pvals.loc[b, a] = p

    return pvals

pearson_p = correlation_pvalues(scores[constructs], "pearson")
spearman_p = correlation_pvalues(scores[constructs], "spearman")

# --------------------------------------------------
# 2. REGRESSION MODELS
# CS predicted by four antecedents.
# BC and PI predicted by CS.
# HC3 robust standard errors are used.
# --------------------------------------------------

models = {
    "CS_model": ("CS", ["PA", "ACA", "CT", "PSR"]),
    "BC_model": ("BC", ["CS"]),
    "PI_model": ("PI", ["CS"]),
}

regression_rows = []
vif_rows = []
diagnostic_rows = []
model_summaries = {}

for model_name, (outcome, predictors) in models.items():
    X = sm.add_constant(scores[predictors])
    y = scores[outcome]

    model = sm.OLS(y, X).fit(cov_type="HC3")
    model_summaries[model_name] = model

    for term in model.params.index:
        regression_rows.append({
            "Model": model_name,
            "Outcome": outcome,
            "Predictor": term,
            "Coefficient": model.params[term],
            "Robust_SE": model.bse[term],
            "t_value": model.tvalues[term],
            "p_value": model.pvalues[term],
            "CI_lower": model.conf_int().loc[term, 0],
            "CI_upper": model.conf_int().loc[term, 1],
            "R_squared": model.rsquared,
            "Adjusted_R_squared": model.rsquared_adj,
        })

    if len(predictors) > 1:
        for i, predictor in enumerate(predictors, start=1):
            vif_rows.append({
                "Model": model_name,
                "Predictor": predictor,
                "VIF": variance_inflation_factor(
                    X.values, i
                ),
            })

    # Residual diagnostics
    bp_lm, bp_p, _, _ = het_breuschpagan(
        model.resid, model.model.exog
    )

    diagnostic_rows.append({
        "Model": model_name,
        "Breusch_Pagan_LM": bp_lm,
        "Breusch_Pagan_p": bp_p,
        "Residual_mean": np.mean(model.resid),
        "Residual_SD": np.std(model.resid, ddof=1),
    })

# --------------------------------------------------
# 3. EXPORT RESULTS
# --------------------------------------------------

output_file = OUT_DIR / "stage3_relationship_results.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    pearson.to_excel(writer, sheet_name="Pearson_Correlations")
    pearson_p.to_excel(writer, sheet_name="Pearson_pvalues")
    spearman.to_excel(writer, sheet_name="Spearman_Correlations")
    spearman_p.to_excel(writer, sheet_name="Spearman_pvalues")

    pd.DataFrame(regression_rows).to_excel(
        writer, sheet_name="Regression", index=False
    )
    pd.DataFrame(vif_rows).to_excel(
        writer, sheet_name="VIF", index=False
    )
    pd.DataFrame(diagnostic_rows).to_excel(
        writer, sheet_name="Diagnostics", index=False
    )

print("\n========== PEARSON CORRELATIONS ==========")
print(pearson.round(3).to_string())

print("\n========== SPEARMAN CORRELATIONS ==========")
print(spearman.round(3).to_string())

print("\n========== REGRESSION RESULTS ==========")
print(pd.DataFrame(regression_rows).round(4).to_string(index=False))

print("\n========== VIF ==========")
print(pd.DataFrame(vif_rows).round(3).to_string(index=False))

print("\n========== DIAGNOSTICS ==========")
print(pd.DataFrame(diagnostic_rows).round(4).to_string(index=False))

print("\nSaved:", output_file)
