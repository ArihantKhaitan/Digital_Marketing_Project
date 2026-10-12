
from pathlib import Path
import pandas as pd

BASE = Path.cwd()

SKIP_DIRS = {
    ".venv", "venv", "__pycache__", ".git",
    "stage5_diagnostic_plots"
}

KEYWORDS = [
    "age", "gender", "sex", "education", "occupation",
    "income", "country", "city", "demographic",
    "social media", "platform", "frequency", "usage",
    "instagram", "youtube", "influencer"
]

files = []

for path in BASE.rglob("*"):
    if not path.is_file():
        continue

    if any(part in SKIP_DIRS for part in path.parts):
        continue

    if "analysis_outputs" in path.parts:
        continue

    if path.suffix.lower() in [".xlsx", ".xls", ".csv"]:
        files.append(path)

print("\nPROJECT FILE AUDIT")
print("=" * 70)

if not files:
    print("No Excel or CSV files found in:", BASE)

for path in sorted(files):
    print(f"\nFILE: {path.relative_to(BASE)}")

    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, nrows=5)
            columns = list(df.columns)
            print("Format: CSV")
            print("Columns:", columns)

            matched = [
                c for c in columns
                if any(k in str(c).lower() for k in KEYWORDS)
            ]
            print("Potential demographic columns:", matched)

        else:
            excel = pd.ExcelFile(path)
            print("Sheets:", excel.sheet_names)

            for sheet in excel.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet, nrows=5)
                columns = list(df.columns)

                print(f"\n  SHEET: {sheet}")
                print("  Columns:", columns)

                matched = [
                    c for c in columns
                    if any(k in str(c).lower() for k in KEYWORDS)
                ]
                print("  Potential demographic columns:", matched)

    except Exception as exc:
        print("Could not inspect this file:", exc)

print("\nAUDIT COMPLETE — no files were changed.")
