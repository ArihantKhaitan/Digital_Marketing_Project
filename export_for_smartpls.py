
from pathlib import Path
import pandas as pd

base_dir = Path(__file__).resolve().parent

input_file = (
    base_dir / "analysis_outputs" / "main_study_numeric.xlsx"
)

output_file = (
    base_dir / "analysis_outputs" / "smartpls_import.csv"
)

# Read the questionnaire item responses
df = pd.read_excel(
    input_file,
    sheet_name="Numeric_Items"
)

# Keep only the 26 measurement items.
# QC1 is an attention-check question, not a construct indicator.
constructs = {
    "PA": ["PA1", "PA2", "PA3", "PA4"],
    "ACA": ["ACA1", "ACA2", "ACA3", "ACA4"],
    "CT": ["CT1", "CT2", "CT3", "CT4"],
    "PSR": ["PSR1", "PSR2", "PSR3", "PSR4"],
    "CS": ["CS1", "CS2", "CS3", "CS4"],
    "BC": ["BC1", "BC2", "BC3"],
    "PI": ["PI1", "PI2", "PI3"],
}

columns = [
    item
    for item_list in constructs.values()
    for item in item_list
]

missing = [c for c in columns if c not in df.columns]
if missing:
    raise ValueError(f"Missing questionnaire columns: {missing}")

data = df[columns].copy()

if data.isna().any().any():
    raise ValueError("Missing responses found in the 26 items.")

if not data.isin([1, 2, 3, 4, 5]).all().all():
    raise ValueError("Unexpected values found. Check the coding.")

data.to_csv(output_file, index=False, encoding="utf-8-sig")

print("Export successful!")
print("Rows:", len(data))
print("Measurement items:", len(columns))
print("Saved to:", output_file)
