
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm

from scipy.stats import chi2, norm
from statsmodels.stats.outliers_influence import OLSInfluence

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE = Path.cwd()
OUT = BASE / "analysis_outputs"
OUT.mkdir(exist_ok=True)

DATA_FILE = OUT / "main_study_numeric.xlsx"
RESULT_FILE = OUT / "stage5_missing_checks.xlsx"
PLOT_DIR = OUT / "stage5_diagnostic_plots"
PLOT_DIR.mkdir(exist_ok=True)

CONSTRUCTS = ["PA", "ACA", "CT", "PSR", "CS", "BC", "PI"]

ITEMS = (
    [f"PA{i}" for i in range(1, 5)]
    + [f"ACA{i}" for i in range(1, 5)]
    + [f"CT{i}" for i in range(1, 5)]
    + [f"PSR{i}" for i in range(1, 5)]
    + [f"CS{i}" for i in range(1, 5)]
    + [f"BC{i}" for i in range(1, 4)]
    + [f"PI{i}" for i in range(1, 4)]
)

# --------------------------------------------------
# 1. Read the 26 questionnaire indicators
# --------------------------------------------------
if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {DATA_FILE}. "
        "Check that main_study_numeric.xlsx is in analysis_outputs."
    )

items_df = pd.read_excel(DATA_FILE, sheet_name="Numeric_Items")

missing_columns = [c for c in ITEMS if c not in items_df.columns]
if missing_columns:
    raise ValueError(f"Missing expected item columns: {missing_columns}")

X = items_df[ITEMS].apply(pd.to_numeric, errors="coerce").dropna()

if len(X) < 3:
    raise ValueError("Not enough complete cases for multivariate analysis.")

# --------------------------------------------------
# 2. Mardia multivariate normality tests
# --------------------------------------------------
A = X.to_numpy(dtype=float)
n, p = A.shape

centered = A - A.mean(axis=0)
cov = np.cov(centered, rowvar=False, ddof=1)
inv_cov = np.linalg.pinv(cov)

# Squared Mahalanobis distances
md2 = np.einsum("ij,jk,ik->i", centered, inv_cov, centered)

# Pairwise cross-products for Mardia's multivariate skewness
cross = centered @ inv_cov @ centered.T
b1p = np.mean(cross ** 3)

# Mardia's multivariate kurtosis
b2p = np.mean(md2 ** 2)

# Large-sample reference tests
df_skew = p * (p + 1) * (p + 2) // 6
skew_stat = n * b1p / 6
skew_p = chi2.sf(skew_stat, df_skew)

expected_kurt = p * (p + 2)
kurt_z = (b2p - expected_kurt) / np.sqrt(
    8 * p * (p + 2) / n
)
kurt_p = 2 * norm.sf(abs(kurt_z))

mardia = pd.DataFrame([
    {
        "Test": "Mardia multivariate skewness",
        "Statistic": b1p,
        "Reference_statistic": skew_stat,
        "Degrees_of_freedom": df_skew,
        "p_value": skew_p,
        "N": n,
        "Variables": p,
    },
    {
        "Test": "Mardia multivariate kurtosis",
        "Statistic": b2p,
        "Reference_statistic": kurt_z,
        "Degrees_of_freedom": np.nan,
        "p_value": kurt_p,
        "N": n,
        "Variables": p,
    },
])

# --------------------------------------------------
# 3. Recreate the three regression models
# --------------------------------------------------
construct_scores = pd.read_excel(
    OUT / "stage2_statistical_results.xlsx",
    sheet_name="Construct_Scores"
)

if not all(c in construct_scores.columns for c in CONSTRUCTS):
    raise ValueError("Expected construct scores are missing.")

models = {
    "CS_model": ("CS", ["PA", "ACA", "CT", "PSR"]),
    "BC_model": ("BC", ["CS"]),
    "PI_model": ("PI", ["CS"]),
}

diagnostics = []

for name, (outcome, predictors) in models.items():
    df = construct_scores[[outcome] + predictors].dropna()
    y = df[outcome]
    design = sm.add_constant(df[predictors], has_constant="add")

    model = sm.OLS(y, design).fit()
    influence = OLSInfluence(model)

    fitted = model.fittedvalues
    residuals = model.resid
    studentized = influence.resid_studentized_external
    cooks_d = influence.cooks_distance[0]

    diagnostics.append({
        "Model": name,
        "N": int(model.nobs),
        "R_squared": model.rsquared,
        "Adjusted_R_squared": model.rsquared_adj,
        "Maximum_absolute_studentized_residual":
            float(np.max(np.abs(studentized))),
        "Observations_abs_studentized_residual_gt_3":
            int(np.sum(np.abs(studentized) > 3)),
        "Maximum_Cooks_distance": float(np.max(cooks_d)),
        "Cook_distance_threshold_4_over_n":
            float(4 / model.nobs),
        "Observations_Cook_distance_gt_4_over_n":
            int(np.sum(cooks_d > 4 / model.nobs)),
    })

    # Residuals versus fitted values
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(fitted, residuals, alpha=0.65)
    ax.axhline(0, linestyle="--")
    ax.set_title(f"{name}: residuals versus fitted")
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / f"{name}_residuals_vs_fitted.png", dpi=160)
    plt.close(fig)

    # Normal Q-Q plot of regression residuals
    fig = sm.qqplot(residuals, line="45", fit=True)
    fig.suptitle(f"{name}: residual Q-Q plot")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / f"{name}_residual_qq.png", dpi=160)
    plt.close(fig)

    # Cook's distance plot
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.stem(np.arange(1, len(cooks_d) + 1), cooks_d)
    ax.axhline(4 / model.nobs, linestyle="--")
    ax.set_title(f"{name}: Cook's distance")
    ax.set_xlabel("Observation number")
    ax.set_ylabel("Cook's distance")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / f"{name}_cooks_distance.png", dpi=160)
    plt.close(fig)

# --------------------------------------------------
# 4. Save results
# --------------------------------------------------
with pd.ExcelWriter(RESULT_FILE, engine="openpyxl") as writer:
    mardia.to_excel(writer, sheet_name="Mardia_Normality", index=False)
    pd.DataFrame(diagnostics).to_excel(
        writer, sheet_name="Regression_Diagnostics", index=False
    )

print("\nDiagnostic checks completed.")
print(f"Complete cases for Mardia test: {n}")
print(f"Number of indicators: {p}")
print("\nMardia results:")
print(mardia.to_string(index=False))
print("\nRegression diagnostics:")
print(pd.DataFrame(diagnostics).to_string(index=False))
print(f"\nResults saved to: {RESULT_FILE}")
print(f"Plots saved to: {PLOT_DIR}")
