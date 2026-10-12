
from pathlib import Path
import pandas as pd
import numpy as np

# ==================================================
# 1. FILE PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / (
    "Influencer Authenticity vs. AI-Generated "
    "Content Main Study (Responses).xlsx"
)

OUTPUT_DIR = BASE_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find the Excel file:\n{INPUT_FILE}\n"
        "Place it in the same folder as this script."
    )

# ==================================================
# 2. LOAD AND CHECK DATA
# ==================================================

original = pd.read_excel(INPUT_FILE)

print("\n========== DATASET CHECK ==========")
print("Original rows:", len(original))
print("Original columns:", len(original.columns))

# Remove completely empty columns only.
df = original.dropna(axis=1, how="all").copy()

# Map each construct to its questionnaire section.
sections = {
    "PA": "Section C",
    "ACA": "Section D",
    "CT": "Section E",
    "PSR": "Section F",
    "CS": "Section G",
    "BC": "Section H",
    "PI": "Section I",
}

expected_counts = {
    "PA": 4,
    "ACA": 4,
    "CT": 4,
    "PSR": 4,
    "CS": 4,
    "BC": 3,
    "PI": 3,
}

item_columns = {
    name: [
        col for col in df.columns
        if col.startswith(section)
    ]
    for name, section in sections.items()
}

for name, expected in expected_counts.items():
    actual = len(item_columns[name])
    print(f"{name}: {actual} items")

    if actual != expected:
        raise ValueError(
            f"{name} has {actual} items; "
            f"expected {expected}. Check column names."
        )

all_items = [
    col
    for name in sections
    for col in item_columns[name]
]

assert len(all_items) == 26

# Find screening and quality-check columns.
consent_col = next(
    c for c in df.columns
    if c.startswith("1. I agree to participate")
)
follow_col = next(
    c for c in df.columns
    if c.startswith("2. Do you follow")
)
exposure_col = next(
    c for c in df.columns
    if c.startswith("3. Have you seen")
)
qc_col = next(
    c for c in df.columns
    if "QC1." in c
)

# ==================================================
# 3. SCREENING AND COMPLETENESS AUDIT
# ==================================================

audit = pd.DataFrame(index=df.index)

audit["measurement_items_answered"] = (
    df[all_items].notna().sum(axis=1)
)
audit["all_26_items_complete"] = (
    audit["measurement_items_answered"] == 26
)
audit["consent_yes"] = (
    df[consent_col].astype(str).str.strip().str.lower()
    == "yes"
)
audit["follows_influencer_yes"] = (
    df[follow_col].astype(str).str.strip().str.lower()
    == "yes"
)
audit["recent_exposure_yes"] = (
    df[exposure_col].astype(str).str.strip().str.lower()
    == "yes"
)

# Exact duplicates are flagged, not automatically deleted.
audit["exact_duplicate_after_first"] = (
    df.duplicated(keep="first")
)

# ==================================================
# 4. CONVERT LIKERT RESPONSES TO NUMBERS
# Example: "5 - Strongly Agree" becomes 5.
# ==================================================

numeric = pd.DataFrame(index=df.index)

for col in all_items + [qc_col]:
    extracted = df[col].astype("string").str.extract(
        r"^\s*([1-5])(?:\s*-|\s*$)",
        expand=False
    )

    numeric[col] = pd.to_numeric(
        extracted, errors="coerce"
    )

# Rename items to short codes in questionnaire order.
rename_map = {}

for name, cols in item_columns.items():
    for i, col in enumerate(cols, start=1):
        rename_map[col] = f"{name}{i}"

numeric = numeric.rename(columns=rename_map)
numeric = numeric.rename(columns={qc_col: "QC1"})

# Stop if any non-missing original answer could not
# be converted to a valid Likert number.
conversion_errors = {}

for col in all_items + [qc_col]:
    bad = df[col].notna() & numeric[
        rename_map.get(col, "QC1")
    ].isna()

    if bad.any():
        conversion_errors[col] = int(bad.sum())

if conversion_errors:
    print("\nConversion errors:", conversion_errors)
    raise ValueError(
        "Some answers could not be converted. "
        "Inspect the source responses before continuing."
    )

# ==================================================
# 5. CHECK ATTENTION CHECK
# QC1 asks whether the respondent carefully read
# the survey. A low score is flagged for review,
# not automatically excluded.
# ==================================================

audit["QC1_numeric"] = numeric["QC1"]
audit["QC1_low_response_flag"] = numeric["QC1"] <= 2

# ==================================================
# 6. CALCULATE CONSTRUCT SCORES
# Scores are means of each construct's items.
# All 26 measurement items must be present.
# ==================================================

scores = pd.DataFrame(index=df.index)

for name in sections:
    codes = [
        rename_map[col] for col in item_columns[name]
    ]

    scores[name] = numeric[codes].mean(axis=1)

    # Explicitly require every item for the construct.
    scores.loc[numeric[codes].isna().any(axis=1), name] = (
        np.nan
    )

# ==================================================
# 7. CREATE SUMMARY TABLES
# ==================================================

summary = pd.DataFrame({
    "Check": [
        "Total responses",
        "Complete measurement responses",
        "Incomplete measurement responses",
        "Consent = Yes",
        "Follow an influencer = Yes",
        "Recent influencer-content exposure = Yes",
        "Exact duplicate rows after first occurrence",
        "QC1 responses <= 2 (flagged for review)",
    ],
    "Count": [
        len(df),
        int(audit["all_26_items_complete"].sum()),
        int((~audit["all_26_items_complete"]).sum()),
        int(audit["consent_yes"].sum()),
        int(audit["follows_influencer_yes"].sum()),
        int(audit["recent_exposure_yes"].sum()),
        int(audit["exact_duplicate_after_first"].sum()),
        int(audit["QC1_low_response_flag"].sum()),
    ],
})

demographic_columns = [
    c for c in df.columns
    if c.startswith((
        "4. Age:",
        "5. Gender:",
        "6. How often",
        "7. Which platforms",
    ))
]

# ==================================================
# 8. SAVE OUTPUTS
# ==================================================

audit["source_excel_row"] = np.arange(2, len(df) + 2)

audit_path = OUTPUT_DIR / "initial_data_audit.xlsx"
coded_path = OUTPUT_DIR / "main_study_numeric.xlsx"

with pd.ExcelWriter(audit_path, engine="openpyxl") as writer:
    summary.to_excel(
        writer, sheet_name="Summary", index=False
    )
    audit.to_excel(
        writer, sheet_name="Row_Audit", index=False
    )
    df.to_excel(
        writer, sheet_name="Original_Data", index=False
    )

with pd.ExcelWriter(coded_path, engine="openpyxl") as writer:
    numeric.to_excel(
        writer, sheet_name="Numeric_Items", index=False
    )
    scores.to_excel(
        writer, sheet_name="Construct_Scores", index=False
    )

    for col in demographic_columns:
        frequency = (
            df[col].value_counts(dropna=False)
            .rename_axis("Response")
            .reset_index(name="Count")
        )
        sheet = {
            "4. Age:": "Age",
            "5. Gender:": "Gender",
            "6. How often do you use social media?": "Usage",
            "7. Which platforms do you use most?": "Platforms",
        }.get(col, "Demographic")[:31]

        frequency.to_excel(
            writer, sheet_name=sheet, index=False
        )

print("\n========== AUDIT SUMMARY ==========")
print(summary.to_string(index=False))

print("\nFiles created:")
print(audit_path)
print(coded_path)

print("\nData preparation completed.")
print("No respondent rows were automatically removed.")
