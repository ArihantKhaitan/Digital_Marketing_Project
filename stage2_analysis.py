
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "analysis_outputs" / "main_study_numeric.xlsx"
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE}. "
        "Check the output folder and filename."
    )

# --------------------------------------------------
# 1. LOAD CODED QUESTIONNAIRE ITEMS
# --------------------------------------------------

items = pd.read_excel(INPUT_FILE, sheet_name="Numeric_Items")

constructs = {
    "PA": ["PA1", "PA2", "PA3", "PA4"],
    "ACA": ["ACA1", "ACA2", "ACA3", "ACA4"],
    "CT": ["CT1", "CT2", "CT3", "CT4"],
    "PSR": ["PSR1", "PSR2", "PSR3", "PSR4"],
    "CS": ["CS1", "CS2", "CS3", "CS4"],
    "BC": ["BC1", "BC2", "BC3"],
    "PI": ["PI1", "PI2", "PI3"],
}

all_items = [
    item for group in constructs.values() for item in group
]

# Require valid numeric responses for all 26 items.
items[all_items] = items[all_items].apply(
    pd.to_numeric, errors="coerce"
)

if items[all_items].isna().any().any():
    raise ValueError(
        "Missing or invalid item values detected. "
        "Resolve these before continuing."
    )

if not items[all_items].isin([1, 2, 3, 4, 5]).all().all():
    raise ValueError("Found values outside the 1–5 scale.")

n = len(items)
print(f"Analysing {n} complete responses.")

# --------------------------------------------------
# 2. DESCRIPTIVE STATISTICS
# --------------------------------------------------

scores = pd.DataFrame(index=items.index)

for name, cols in constructs.items():
    scores[name] = items[cols].mean(axis=1)

desc = scores.agg(
    ["count", "mean", "std", "min", "median", "max"]
).T

desc["skewness"] = scores.apply(
    lambda x: stats.skew(x, bias=False)
)
desc["excess_kurtosis"] = scores.apply(
    lambda x: stats.kurtosis(x, bias=False)
)

item_desc = items[all_items].agg(
    ["mean", "std", "min", "max"]
).T
item_desc["skewness"] = items[all_items].apply(
    lambda x: stats.skew(x, bias=False)
)
item_desc["excess_kurtosis"] = items[all_items].apply(
    lambda x: stats.kurtosis(x, bias=False)
)

# --------------------------------------------------
# 3. CRONBACH'S ALPHA
# --------------------------------------------------

def cronbach_alpha(data):
    data = data.dropna()
    k = data.shape[1]

    if k < 2:
        return np.nan

    item_variances = data.var(axis=0, ddof=1)
    total_variance = data.sum(axis=1).var(ddof=1)

    if total_variance == 0:
        return np.nan

    return (k / (k - 1)) * (
        1 - item_variances.sum() / total_variance
    )

reliability_rows = []
item_rows = []

for name, cols in constructs.items():
    block = items[cols]
    alpha = cronbach_alpha(block)

    reliability_rows.append({
        "Construct": name,
        "Items": len(cols),
        "Cronbach_alpha": alpha,
        "Mean_construct_score": scores[name].mean(),
        "SD_construct_score": scores[name].std(ddof=1),
    })

    for item in cols:
        remaining = [c for c in cols if c != item]
        corrected_total = block[remaining].sum(axis=1)

        corr = stats.pearsonr(
            block[item], corrected_total
        ).statistic

        reduced_alpha = cronbach_alpha(block[remaining])

        item_rows.append({
            "Construct": name,
            "Item": item,
            "Item_mean": block[item].mean(),
            "Item_SD": block[item].std(ddof=1),
            "Corrected_item_total_correlation": corr,
            "Alpha_if_item_deleted": reduced_alpha,
        })

reliability = pd.DataFrame(reliability_rows)
item_stats = pd.DataFrame(item_rows)

# --------------------------------------------------
# 4. NORMALITY DIAGNOSTICS
# Likert-derived construct scores are bounded and
# discrete. Do not use a single p-value as the verdict.
# --------------------------------------------------

normality_rows = []

for name in constructs:
    x = scores[name]

    normality_rows.append({
        "Construct": name,
        "N": len(x),
        "Skewness": stats.skew(x, bias=False),
        "Excess_kurtosis": stats.kurtosis(x, bias=False),
        "Shapiro_W": stats.shapiro(x).statistic,
        "Shapiro_p": stats.shapiro(x).pvalue,
    })

normality = pd.DataFrame(normality_rows)

# Save histograms and Q-Q plots for visual inspection.
for name in constructs:
    x = scores[name]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].hist(x, bins=np.arange(0.75, 5.76, 0.5))
    axes[0].set_title(f"{name}: score distribution")
    axes[0].set_xlabel("Construct mean (1–5)")
    axes[0].set_ylabel("Frequency")

    stats.probplot(x, dist="norm", plot=axes[1])
    axes[1].set_title(f"{name}: normal Q-Q plot")

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"normality_{name}.png", dpi=150)
    plt.close(fig)

# --------------------------------------------------
# 5. HARMAN'S SINGLE-FACTOR TEST
# Exploratory, unrotated PCA on standardized items.
# This is a limited common-method-bias diagnostic.
# --------------------------------------------------

standardized = StandardScaler().fit_transform(items[all_items])

pca = PCA()
pca.fit(standardized)

first_factor_pct = pca.explained_variance_ratio_[0] * 100

harman = pd.DataFrame({
    "Measure": [
        "Number of respondents",
        "Number of measurement items",
        "First unrotated component variance explained (%)",
    ],
    "Value": [n, len(all_items), first_factor_pct],
})

eigenvalues = pd.DataFrame({
    "Component": np.arange(1, len(all_items) + 1),
    "Eigenvalue": pca.explained_variance_,
    "Variance_explained_pct": pca.explained_variance_ratio_ * 100,
    "Cumulative_variance_pct": (
        np.cumsum(pca.explained_variance_ratio_) * 100
    ),
})

# --------------------------------------------------
# 6. EXPORT TABLES
# --------------------------------------------------

output_file = OUTPUT_DIR / "stage2_statistical_results.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    desc.to_excel(writer, sheet_name="Construct_Descriptives")
    item_desc.to_excel(writer, sheet_name="Item_Descriptives")
    reliability.to_excel(writer, sheet_name="Reliability", index=False)
    item_stats.to_excel(writer, sheet_name="Item_Total_Stats", index=False)
    normality.to_excel(writer, sheet_name="Normality", index=False)
    harman.to_excel(writer, sheet_name="Harman_Test", index=False)
    eigenvalues.to_excel(writer, sheet_name="PCA_Components", index=False)
    scores.to_excel(writer, sheet_name="Construct_Scores", index=False)

print("\n========== CONSTRUCT DESCRIPTIVES ==========")
print(desc.round(3).to_string())

print("\n========== RELIABILITY ==========")
print(reliability.round(3).to_string(index=False))

print("\n========== ITEM-TOTAL STATISTICS ==========")
print(item_stats.round(3).to_string(index=False))

print("\n========== NORMALITY DIAGNOSTICS ==========")
print(normality.round(4).to_string(index=False))

print("\nHarman first-component variance explained:",
      round(first_factor_pct, 2), "%")

print("\nResults saved to:", output_file)
print("Normality plots saved in:", OUTPUT_DIR)
