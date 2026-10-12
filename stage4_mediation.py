
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

# ==================================================
# MEDIATION: 5,000 BOOTSTRAP RESAMPLES
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = (
    BASE_DIR / "analysis_outputs"
    / "stage2_statistical_results.xlsx"
)
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

N_BOOT = 5000
SEED = 2026
ALPHA = 0.05

df = pd.read_excel(
    INPUT_FILE, sheet_name="Construct_Scores"
)

antecedents = ["PA", "ACA", "CT", "PSR"]
mediator = "CS"
outcomes = ["BC", "PI"]
required = antecedents + [mediator] + outcomes

df = df[required].apply(pd.to_numeric, errors="coerce")
df = df.dropna().reset_index(drop=True)

if len(df) < 50:
    raise ValueError("Too few complete observations.")

print(f"Sample size used: {len(df)}")
print(f"Bootstrap resamples: {N_BOOT}")


# OLS coefficients calculated with least squares.
# The first column is the intercept.
def ols_coefficients(y, X):
    X_design = np.column_stack([
        np.ones(len(X)), X
    ])
    return np.linalg.lstsq(
        X_design, y, rcond=None
    )[0]


# Bias-corrected bootstrap confidence interval.
def bias_corrected_ci(bootstrap_values, observed, alpha=0.05):
    boot = np.asarray(bootstrap_values)
    boot = boot[np.isfinite(boot)]

    if len(boot) < 100:
        return np.nan, np.nan

    # Proportion of bootstrap estimates below observed estimate.
    proportion = np.mean(boot < observed)

    # Avoid infinite z-scores at the endpoints.
    proportion = np.clip(
        proportion, 1 / (2 * len(boot)),
        1 - 1 / (2 * len(boot))
    )

    z0 = norm.ppf(proportion)

    z_low = norm.ppf(alpha / 2)
    z_high = norm.ppf(1 - alpha / 2)

    q_low = norm.cdf(2 * z0 + z_low)
    q_high = norm.cdf(2 * z0 + z_high)

    lower, upper = np.quantile(
        boot, [q_low, q_high]
    )

    return lower, upper


# ==================================================
# OBSERVED INDIRECT EFFECTS
# ==================================================

X_all = df[antecedents].to_numpy()
CS = df[mediator].to_numpy()

# Mediator model: CS ~ PA + ACA + CT + PSR
a_coefficients = ols_coefficients(CS, X_all)

# a_coefficients[0] is intercept.
# Remaining coefficients correspond to antecedents.
a_values = dict(zip(antecedents, a_coefficients[1:]))

observed = {}

for outcome in outcomes:
    Y = df[outcome].to_numpy()

    # Outcome model: Y ~ CS + PA + ACA + CT + PSR
    outcome_predictors = np.column_stack([CS, X_all])
    b_coefficients = ols_coefficients(
        Y, outcome_predictors
    )

    b_value = b_coefficients[1]  # CS coefficient

    for i, x in enumerate(antecedents):
        indirect = a_values[x] * b_value

        observed[(x, outcome)] = {
            "a_path": a_values[x],
            "b_path": b_value,
            "indirect_effect": indirect,
        }


# ==================================================
# BOOTSTRAP INDIRECT EFFECTS
# Resample respondents with replacement.
# ==================================================

rng = np.random.default_rng(SEED)
boot_results = {
    key: [] for key in observed
}

n = len(df)

for iteration in range(N_BOOT):
    idx = rng.integers(0, n, size=n)

    sample = df.iloc[idx]

    xb = sample[antecedents].to_numpy()
    csb = sample[mediator].to_numpy()

    # Estimate antecedent -> mediator paths.
    a_boot = ols_coefficients(csb, xb)[1:]

    for outcome in outcomes:
        yb = sample[outcome].to_numpy()

        # Estimate mediator -> outcome, adjusting for
        # the four antecedents.
        outcome_x = np.column_stack([csb, xb])
        b_boot = ols_coefficients(
            yb, outcome_x
        )[1]

        for i, x in enumerate(antecedents):
            boot_results[(x, outcome)].append(
                a_boot[i] * b_boot
            )

    if (iteration + 1) % 500 == 0:
        print(f"Completed {iteration + 1}/{N_BOOT}")

# ==================================================
# RESULTS TABLE
# ==================================================

rows = []

for key, result in observed.items():
    x, outcome = key
    boot = np.asarray(boot_results[key])

    lower, upper = bias_corrected_ci(
        boot, result["indirect_effect"], ALPHA
    )

    rows.append({
        "Antecedent": x,
        "Mediator": mediator,
        "Outcome": outcome,
        "a_path": result["a_path"],
        "b_path": result["b_path"],
        "Indirect_effect": result["indirect_effect"],
        "BC_95CI_lower": lower,
        "BC_95CI_upper": upper,
        "Bootstrap_resamples": N_BOOT,
        "CI_excludes_zero": (
            lower > 0 or upper < 0
        ),
    })

results = pd.DataFrame(rows)

output_file = (
    OUTPUT_DIR / "stage4_mediation_results.xlsx"
)
with pd.ExcelWriter(
    output_file, engine="openpyxl"
) as writer:
    results.to_excel(
        writer, sheet_name="Indirect_Effects",
        index=False
    )

print("\n========== MEDIATION RESULTS ==========")
print(results.round(4).to_string(index=False))
print("\nSaved to:", output_file)
