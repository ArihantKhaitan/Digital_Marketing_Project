
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "analysis_outputs" / "main_study_numeric.xlsx"
OUTPUT_DIR = BASE / "analysis_outputs"
OUTPUT_FILE = OUTPUT_DIR / "stage9_predictive_results.xlsx"

# Seven reflective constructs and their indicators
ITEMS = {
    "PA":  ["PA1", "PA2", "PA3", "PA4"],
    "ACA": ["ACA1", "ACA2", "ACA3", "ACA4"],
    "CT":  ["CT1", "CT2", "CT3", "CT4"],
    "PSR": ["PSR1", "PSR2", "PSR3", "PSR4"],
    "CS":  ["CS1", "CS2", "CS3", "CS4"],
    "BC":  ["BC1", "BC2", "BC3"],
    "PI":  ["PI1", "PI2", "PI3"],
}

# Structural model: preserve the specified paths
PREDICTORS = {
    "CS": ["PA", "ACA", "CT", "PSR"],
    "BC": ["CS"],
    "PI": ["CS"],
}

def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Check that main_study_numeric.xlsx is in analysis_outputs."
        )

    # Read the prepared numeric item dataset
    xls = pd.ExcelFile(DATA_FILE)
    sheet = "Numeric_Items" if "Numeric_Items" in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(DATA_FILE, sheet_name=sheet)

    # Accommodate harmless column-name whitespace
    df.columns = df.columns.astype(str).str.strip()

    expected = [item for items in ITEMS.values() for item in items]
    missing = [item for item in expected if item not in df.columns]
    if missing:
        raise ValueError(
            f"Missing indicator columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    data = df[expected].apply(pd.to_numeric, errors="coerce")
    if data.isna().any().any():
        raise ValueError(
            "Missing/non-numeric item values found. Resolve these before "
            "running the assessment; this script does not impute responses."
        )

    if not data.isin([1, 2, 3, 4, 5]).all().all():
        raise ValueError("Unexpected values detected; expected Likert values 1–5.")

    # Check the construct and path specification
    if len(data) != 395:
        print(f"WARNING: Expected 395 rows; found {len(data)}.")

    print(f"Dataset: {DATA_FILE}")
    print(f"Rows: {len(data)} | Indicators: {len(expected)}")
    print("Method: 10-fold cross-validated indicator prediction")
    print("Targets: CS, BC, PI")

    cv = KFold(n_splits=10, shuffle=True, random_state=42)
    item_results = []
    construct_results = []

    for target, predictor_constructs in PREDICTORS.items():
        target_items = ITEMS[target]
        predictor_items = [
            item
            for construct in predictor_constructs
            for item in ITEMS[construct]
        ]

        all_actual = []
        all_predicted = []
        all_baseline = []

        for item in target_items:
            actual_all = []
            predicted_all = []
            baseline_all = []

            for train_idx, test_idx in cv.split(data):
                train = data.iloc[train_idx]
                test = data.iloc[test_idx]

                # Composite scores calculated separately in each fold
                X_train = pd.DataFrame({
                    c: train[ITEMS[c]].mean(axis=1)
                    for c in predictor_constructs
                })
                X_test = pd.DataFrame({
                    c: test[ITEMS[c]].mean(axis=1)
                    for c in predictor_constructs
                })

                y_train = train[item].to_numpy()
                y_test = test[item].to_numpy()

                model = LinearRegression()
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                # Training-fold mean is the reference prediction
                y_base = np.full(len(y_test), y_train.mean())

                actual_all.extend(y_test)
                predicted_all.extend(y_pred)
                baseline_all.extend(y_base)

                actual_all_item = np.asarray(y_test)
                predicted_all_item = np.asarray(y_pred)
                baseline_all_item = np.asarray(y_base)

                actual_item_ss = np.sum(
                    (actual_all_item - y_train.mean()) ** 2
                )
                item_sse = np.sum(
                    (actual_all_item - predicted_all_item) ** 2
                )
                item_sso = actual_item_ss

                actual_all_item_rmse = mean_squared_error(
                    actual_all_item, predicted_all_item
                ) ** 0.5
                actual_all_item_mae = mean_absolute_error(
                    actual_all_item, predicted_all_item
                )

                # Save fold-level predictions for a transparent audit trail
                item_results.append({
                    "Target_construct": target,
                    "Target_item": item,
                    "Fold": len([
                        r for r in item_results
                        if r["Target_construct"] == target
                        and r["Target_item"] == item
                    ]) + 1,
                    "N_test": len(y_test),
                    "SSE": item_sse,
                    "SSO": item_sso,
                    "Q2_predict_fold": (
                        1 - item_sse / item_sso if item_sso > 0 else np.nan
                    ),
                    "RMSE_fold": actual_all_item_rmse,
                    "MAE_fold": actual_all_item_mae,
                })

            # Aggregate out-of-fold predictions for this indicator
            y = np.asarray(actual_all)
            pred = np.asarray(predicted_all)
            base = np.asarray(baseline_all)

            sse = np.sum((y - pred) ** 2)
            sso = np.sum((y - base) ** 2)
            q2 = 1 - sse / sso if sso > 0 else np.nan

            # The baseline is the fold-specific training mean
            item_results.append({
                "Target_construct": target,
                "Target_item": item,
                "Fold": "OVERALL",
                "N_test": len(y),
                "SSE": sse,
                "SSO": sso,
                "Q2_predict_fold": q2,
                "RMSE_fold": mean_squared_error(y, pred) ** 0.5,
                "MAE_fold": mean_absolute_error(y, pred),
            })

            all_actual.extend([])
            all_predicted.extend([])
            all_baseline.extend([])

        # Aggregate all target indicators for each endogenous construct
        overall = [
            r for r in item_results
            if r["Target_construct"] == target
            and r["Fold"] == "OVERALL"
        ]
        total_sse = sum(r["SSE"] for r in overall)
        total_sso = sum(r["SSO"] for r in overall)
        construct_q2 = (
            1 - total_sse / total_sso if total_sso > 0 else np.nan
        )

        construct_results.append({
            "Endogenous_construct": target,
            "Predictor_constructs": ", ".join(predictor_constructs),
            "Indicators": ", ".join(target_items),
            "N": len(data),
            "Total_SSE": total_sse,
            "Total_SSO": total_sso,
            "Q2_predict_approx": construct_q2,
            "Interpretation": (
                "Positive predictive statistic versus mean baseline"
                if construct_q2 > 0
                else "No improvement over mean baseline"
            ) if pd.notna(construct_q2) else "Undefined",
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        pd.DataFrame(construct_results).to_excel(
            writer, sheet_name="Construct_Summary", index=False
        )
        pd.DataFrame(item_results).to_excel(
            writer, sheet_name="Indicator_Results", index=False
        )

    print("\nPREDICTIVE ASSESSMENT COMPLETE")
    print(pd.DataFrame(construct_results).to_string(index=False))
    print(f"\nSaved results to: {OUTPUT_FILE}")
    print(
        "\nIMPORTANT: This is a composite-score regression approximation, "
        "not exact PLS-SEM blindfolding or SmartPLS PLSpredict."
    )

if __name__ == "__main__":
    main()
