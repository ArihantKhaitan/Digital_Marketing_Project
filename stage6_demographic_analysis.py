
from pathlib import Path
import pandas as pd
import re

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE = Path.cwd()

SOURCE_FILE = BASE / (
    "Influencer Authenticity vs. AI-Generated Content Main Study "
    "(Responses).xlsx"
)

OUTPUT_DIR = BASE / "analysis_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "stage6_demographic_results.xlsx"

if not SOURCE_FILE.exists():
    raise FileNotFoundError(
        f"Original survey file not found:\n{SOURCE_FILE}"
    )

# Read original responses
df = pd.read_excel(
    SOURCE_FILE,
    sheet_name="Form responses 1"
)

print("Original survey rows:", len(df))
print("Original survey columns:", len(df.columns))


# --------------------------------------------------
# Identify columns by their original question text
# --------------------------------------------------
def find_column(text):
    matches = [
        col for col in df.columns
        if text.lower() in str(col).lower()
    ]

    if not matches:
        print(f"WARNING: Could not find column containing: {text}")
        return None

    if len(matches) > 1:
        print(f"WARNING: Multiple columns matched '{text}': {matches}")

    return matches[0]


column_map = {
    "Age": find_column("4. Age:"),
    "Gender": find_column("5. Gender:"),
    "Social media usage frequency": find_column(
        "6. How often do you use social media?"
    ),
    "Most-used social media platforms": find_column(
        "7. Which platforms do you use most?"
    ),
    "Follows an influencer": find_column(
        "2. Do you follow any social media influencer?"
    ),
    "Saw promoted content in past 6 months": find_column(
        "3. Have you seen influencer-promoted content in the past 6 months?"
    ),
    "Consent": find_column(
        "1. I agree to participate in this survey."
    ),
    "Quality check": find_column(
        "QC1. I carefully read the questions in this survey."
    ),
}


# --------------------------------------------------
# Frequency tables
# --------------------------------------------------
def frequency_table(series, variable_name):
    # Treat empty strings and whitespace as missing
    s = series.astype("string").str.strip()
    s = s.mask(s.eq(""))

    valid = s.dropna()
    counts = valid.value_counts(dropna=False)

    result = pd.DataFrame({
        "Variable": variable_name,
        "Category": counts.index.astype(str),
        "Frequency": counts.values,
        "Percent_of_valid_responses": (
            counts.values / len(valid) * 100
            if len(valid) else []
        ),
    })

    result["Valid_N"] = len(valid)
    result["Missing_N"] = int(s.isna().sum())
    result["Total_N"] = len(s)

    return result


frequency_tables = []
missing_summary = []

for variable, col in column_map.items():
    if col is None:
        continue

    s = df[col].astype("string").str.strip()
    s = s.mask(s.eq(""))

    missing_summary.append({
        "Variable": variable,
        "Original_column": str(col),
        "Total_N": len(df),
        "Valid_N": int(s.notna().sum()),
        "Missing_N": int(s.isna().sum()),
    })

    # Platforms are handled separately because multiple
    # platforms may be selected by one respondent.
    if variable == "Most-used social media platforms":
        continue

    table = frequency_table(s, variable)
    frequency_tables.append(table)


# --------------------------------------------------
# Multiple-response platform table
# --------------------------------------------------
platform_column = column_map["Most-used social media platforms"]

platform_table = pd.DataFrame()

if platform_column is not None:
    platform_series = (
        df[platform_column]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    platform_responses = platform_series.dropna()
    platform_counts = {}

    for response in platform_responses:
        # Google Forms multiple-choice answers are often
        # separated by commas. Also support semicolons/newlines.
        choices = re.split(r"[,;\n]", str(response))

        for choice in choices:
            choice = choice.strip()

            if choice:
                platform_counts[choice] = (
                    platform_counts.get(choice, 0) + 1
                )

    platform_table = pd.DataFrame([
        {
            "Platform": platform,
            "Respondent_count": count,
            "Percent_of_respondents": (
                count / len(platform_responses) * 100
                if len(platform_responses) else 0
            ),
        }
        for platform, count in sorted(
            platform_counts.items(),
            key=lambda item: (-item[1], item[0].lower())
        )
    ])

    if not platform_table.empty:
        platform_table["Valid_platform_question_N"] = len(
            platform_responses
        )
        platform_table["Missing_platform_question_N"] = int(
            platform_series.isna().sum()
        )


# --------------------------------------------------
# Consent and quality-check audit
# --------------------------------------------------
audit_rows = []

for label in ["Consent", "Quality check"]:
    col = column_map[label]

    if col is None:
        continue

    s = df[col].astype("string").str.strip()
    s = s.mask(s.eq(""))

    counts = s.value_counts(dropna=False)

    for category, count in counts.items():
        audit_rows.append({
            "Question": label,
            "Response": (
                "(Missing)" if pd.isna(category) else str(category)
            ),
            "Frequency": int(count),
            "Percent_of_all_rows": count / len(df) * 100,
        })

audit_table = pd.DataFrame(audit_rows)


# --------------------------------------------------
# Export results
# --------------------------------------------------
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

    if frequency_tables:
        pd.concat(
            frequency_tables,
            ignore_index=True
        ).to_excel(
            writer,
            sheet_name="Demographic_Frequencies",
            index=False
        )

    if not platform_table.empty:
        platform_table.to_excel(
            writer,
            sheet_name="Platform_Frequencies",
            index=False
        )

    pd.DataFrame(missing_summary).to_excel(
        writer,
        sheet_name="Missingness_Summary",
        index=False
    )

    audit_table.to_excel(
        writer,
        sheet_name="Consent_QC_Audit",
        index=False
    )

print("\nDEMOGRAPHIC ANALYSIS COMPLETE")
print("Rows analysed:", len(df))
print("Output file:", OUTPUT_FILE)

print("\nMissing-value summary:")
print(pd.DataFrame(missing_summary).to_string(index=False))

print("\nFrequency tables:")
for table in frequency_tables:
    print("\n", table["Variable"].iloc[0])
    print(
        table[
            ["Category", "Frequency", "Percent_of_valid_responses"]
        ].to_string(index=False)
    )

if not platform_table.empty:
    print("\nPlatform frequencies:")
    print(platform_table.to_string(index=False))
