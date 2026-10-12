
from pathlib import Path
import pandas as pd

BASE = Path.cwd()
OUT = BASE / "analysis_outputs"
SOURCE = OUT / "main_study_numeric.xlsx"
OUTPUT = OUT / "stage7_item_frequency_results.xlsx"

construct_items = {
    "PA": [f"PA{i}" for i in range(1, 5)],
    "ACA": [f"ACA{i}" for i in range(1, 5)],
    "CT": [f"CT{i}" for i in range(1, 5)],
    "PSR": [f"PSR{i}" for i in range(1, 5)],
    "CS": [f"CS{i}" for i in range(1, 5)],
    "BC": [f"BC{i}" for i in range(1, 4)],
    "PI": [f"PI{i}" for i in range(1, 4)],
}

if not SOURCE.exists():
    raise FileNotFoundError(f"File not found: {SOURCE}")

df = pd.read_excel(SOURCE, sheet_name="Numeric_Items")

rows = []
summary_rows = []
problems = []

for construct, items in construct_items.items():
    for item in items:
        if item not in df.columns:
            problems.append(f"Missing item column: {item}")
            continue

        values = pd.to_numeric(df[item], errors="coerce")
        valid = values.dropna()

        invalid = valid[~valid.isin([1, 2, 3, 4, 5])]
        if len(invalid):
            problems.append(
                f"{item}: {len(invalid)} values outside the 1-5 scale"
            )

        for rating in [1, 2, 3, 4, 5]:
            count = int((valid == rating).sum())
            rows.append({
                "Construct": construct,
                "Item": item,
                "Response_value": rating,
                "Frequency": count,
                "Percent_of_valid_responses": (
                    count / len(valid) * 100 if len(valid) else 0
                ),
                "Valid_N": len(valid),
                "Missing_N": int(values.isna().sum()),
            })

        summary_rows.append({
            "Construct": construct,
            "Item": item,
            "N": len(valid),
            "Missing_N": int(values.isna().sum()),
            "Mean": valid.mean(),
            "SD": valid.std(ddof=1),
            "Minimum": valid.min() if len(valid) else None,
            "Maximum": valid.max() if len(valid) else None,
        })

frequencies = pd.DataFrame(rows)
item_summary = pd.DataFrame(summary_rows)

with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
    frequencies.to_excel(
        writer, sheet_name="Item_Frequencies", index=False
    )
    item_summary.to_excel(
        writer, sheet_name="Item_Summary", index=False
    )
    pd.DataFrame({"Validation_issue": problems}).to_excel(
        writer, sheet_name="Validation", index=False
    )

print("Item frequency analysis completed.")
print("Responses:", len(df))
print("Items expected:", sum(map(len, construct_items.values())))
print("Items analysed:", len(item_summary))
print("Validation issues:", len(problems))
print("Saved to:", OUTPUT)

if problems:
    print("\nPlease investigate these issues:")
    for problem in problems:
        print("-", problem)
else:
    print("All 26 items exist and contain only valid 1-5 responses or missing values.")
