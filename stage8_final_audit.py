
from pathlib import Path
import pandas as pd

BASE = Path.cwd()
OUT = BASE / "analysis_outputs"

FILES = {
    "numeric_data": OUT / "main_study_numeric.xlsx",
    "stage2": OUT / "stage2_statistical_results.xlsx",
    "stage3": OUT / "stage3_relationship_results.xlsx",
    "stage4": OUT / "stage4_mediation_results.xlsx",
    "stage6": OUT / "stage6_demographic_results.xlsx",
    "stage7": OUT / "stage7_item_frequency_results.xlsx",
}

EXPECTED_ITEMS = (
    [f"PA{i}" for i in range(1, 5)]
    + [f"ACA{i}" for i in range(1, 5)]
    + [f"CT{i}" for i in range(1, 5)]
    + [f"PSR{i}" for i in range(1, 5)]
    + [f"CS{i}" for i in range(1, 5)]
    + [f"BC{i}" for i in range(1, 4)]
    + [f"PI{i}" for i in range(1, 4)]
)

issues = []
checks = []

def record(name, passed, details):
    checks.append({
        "Check": name,
        "Status": "PASS" if passed else "CHECK",
        "Details": details
    })
    if not passed:
        issues.append(name)

# 1. Check expected output files
for name, path in FILES.items():
    record(
        f"File exists: {name}",
        path.exists(),
        str(path)
    )

if not all(path.exists() for path in FILES.values()):
    print(pd.DataFrame(checks).to_string(index=False))
    raise SystemExit(
        "\nSome files are missing. Resolve those before continuing."
    )

# 2. Check numeric dataset
numeric = pd.read_excel(
    FILES["numeric_data"], sheet_name="Numeric_Items"
)

missing_items = [c for c in EXPECTED_ITEMS if c not in numeric.columns]
extra_columns = [c for c in numeric.columns if c not in EXPECTED_ITEMS]

record(
    "All 26 expected items present",
    len(missing_items) == 0,
    f"Missing items: {missing_items}"
)

record(
    "Numeric dataset has 395 rows",
    len(numeric) == 395,
    f"Rows found: {len(numeric)}"
)

if not missing_items:
    values = numeric[EXPECTED_ITEMS].apply(
        pd.to_numeric, errors="coerce"
    )

    record(
        "All item responses are within 1-5 or missing",
        bool(values.isna().equals(
            numeric[EXPECTED_ITEMS].isna()
        )) and bool(
            values.isna().to_numpy().sum()
            == numeric[EXPECTED_ITEMS].isna().to_numpy().sum()
        ) and bool(
            values.stack().isin([1, 2, 3, 4, 5]).all()
        ),
        f"Missing item cells: {int(values.isna().sum().sum())}"
    )

# 3. Check construct scores
scores = pd.read_excel(
    FILES["stage2"], sheet_name="Construct_Scores"
)

expected_constructs = ["PA", "ACA", "CT", "PSR", "CS", "BC", "PI"]

record(
    "Seven construct scores present",
    all(c in scores.columns for c in expected_constructs),
    f"Rows: {len(scores)}; columns: {list(scores.columns)}"
)

record(
    "Construct-score rows match item rows",
    len(scores) == len(numeric),
    f"Construct rows: {len(scores)}; item rows: {len(numeric)}"
)

# 4. Check item-frequency workbook
freq = pd.read_excel(
    FILES["stage7"], sheet_name="Item_Frequencies"
)

record(
    "Frequency table covers 26 items",
    freq["Item"].nunique() == 26,
    f"Unique items: {freq['Item'].nunique()}"
)

frequency_problems = []

for item, group in freq.groupby("Item"):
    total_frequency = int(group["Frequency"].sum())
    valid_n_values = group["Valid_N"].dropna().unique()

    if len(valid_n_values) != 1 or total_frequency != int(valid_n_values[0]):
        frequency_problems.append({
            "Item": item,
            "Frequency_sum": total_frequency,
            "Valid_N_values": list(valid_n_values)
        })

record(
    "Item frequency totals match valid N",
    len(frequency_problems) == 0,
    f"Problem items: {frequency_problems}"
)

# 5. Check regression and mediation coverage
regression = pd.read_excel(
    FILES["stage3"], sheet_name="Regression"
)

model_names = set(regression["Model"].dropna().astype(str))
expected_models = {"CS_model", "BC_model", "PI_model"}

record(
    "Three regression models present",
    expected_models.issubset(model_names),
    f"Models found: {sorted(model_names)}"
)

mediation = pd.read_excel(
    FILES["stage4"], sheet_name="Indirect_Effects"
)

record(
    "Eight mediation paths present",
    len(mediation) == 8,
    f"Indirect-effect rows: {len(mediation)}"
)

record(
    "Mediation uses 5,000 bootstrap resamples",
    mediation["Bootstrap_resamples"].eq(5000).all(),
    f"Values found: {mediation['Bootstrap_resamples'].unique().tolist()}"
)

# 6. Check demographic outputs
demo = pd.read_excel(
    FILES["stage6"], sheet_name="Demographic_Frequencies"
)

missingness = pd.read_excel(
    FILES["stage6"], sheet_name="Missingness_Summary"
)

record(
    "Demographic frequency tables exist",
    len(demo) > 0,
    f"Frequency rows: {len(demo)}"
)

record(
    "Demographic columns have no missing responses",
    bool((missingness["Missing_N"] == 0).all()),
    f"Variables checked: {len(missingness)}"
)

# 7. Write audit report
audit = pd.DataFrame(checks)
audit_file = OUT / "stage8_final_audit.xlsx"
audit.to_excel(audit_file, index=False)

print("\nFINAL CONSISTENCY AUDIT")
print("=" * 75)
print(audit.to_string(index=False))
print("\nChecks requiring attention:", len(issues))
print("Audit workbook:", audit_file)

if issues:
    print("\nPlease investigate the CHECK items before finalising.")
else:
    print("\nAll programmed consistency checks passed.")
