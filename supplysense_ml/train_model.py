"""
SupplySense shared multi-product demand forecasting model.

Usage:
    python train_model.py --data data.csv --output models/supplysense_model.pkl

The script reproduces the preprocessing, daily aggregation, feature engineering,
chronological split, Random Forest training, evaluation, and model-bundle export.
"""

import argparse
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


FEATURES = [
    "Product_ID", "Month", "DayOfWeek", "Lag1",
    "Lag7", "Roll7", "Roll14"
]


def prepare_data(csv_path):
    df = pd.read_csv(csv_path, encoding="latin1")

    required = {"InvoiceNo", "StockCode", "Description", "Quantity",
                "InvoiceDate", "UnitPrice"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    # Remove cancelled invoices and invalid quantities/prices.
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)].copy()

    # The dataset's dates are parsed using month-first interpretation.
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], dayfirst=False, errors="coerce"
    )
    df = df.dropna(subset=["InvoiceDate"]).copy()
    df["StockCode"] = df["StockCode"].astype(str)

    # Aggregate quantity sold per product per calendar day.
    daily = (
        df.groupby(["StockCode", df["InvoiceDate"].dt.normalize()])["Quantity"]
        .sum()
        .reset_index()
    )
    daily.columns = ["StockCode", "Date", "Demand"]

    # Fill missing product-date combinations with zero demand.
    all_dates = pd.date_range(
        start=daily["Date"].min(),
        end=daily["Date"].max(),
        freq="D"
    )
    all_combinations = pd.MultiIndex.from_product(
        [daily["StockCode"].unique(), all_dates],
        names=["StockCode", "Date"]
    )
    daily = (
        daily.set_index(["StockCode", "Date"])
        .reindex(all_combinations, fill_value=0)
        .reset_index()
    )

    # Calendar and product-specific historical demand features.
    daily["Month"] = daily["Date"].dt.month
    daily["DayOfWeek"] = daily["Date"].dt.dayofweek

    grouped = daily.groupby("StockCode")["Demand"]
    daily["Lag1"] = grouped.shift(1)
    daily["Lag7"] = grouped.shift(7)
    daily["Roll7"] = grouped.transform(
        lambda values: values.shift(1).rolling(7).mean()
    )
    daily["Roll14"] = grouped.transform(
        lambda values: values.shift(1).rolling(14).mean()
    )

    model_data = daily.dropna().copy()
    return df, daily, model_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data.csv",
                        help="Path to the Online Retail CSV file")
    parser.add_argument("--output", default="models/supplysense_model.pkl",
                        help="Path for the exported model bundle")
    args = parser.parse_args()

    df, daily, model_data = prepare_data(args.data)
    model_data = model_data.sort_values("Date").reset_index(drop=True)

    # Chronological 80/20 split by unique date, not random row split.
    unique_dates = sorted(model_data["Date"].unique())
    split_index = int(len(unique_dates) * 0.8)
    split_date = unique_dates[split_index]

    train_data = model_data[model_data["Date"] < split_date].copy()
    test_data = model_data[model_data["Date"] >= split_date].copy()

    # Encode product codes consistently for model training and inference.
    product_encoder = LabelEncoder()
    product_encoder.fit(model_data["StockCode"])
    train_data["Product_ID"] = product_encoder.transform(train_data["StockCode"])
    test_data["Product_ID"] = product_encoder.transform(test_data["StockCode"])

    X_train = train_data[FEATURES]
    y_train = train_data["Demand"]
    X_test = test_data[FEATURES]
    y_test = test_data["Demand"]

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print("\nOverall one-step-ahead test metrics")
    print(f"MAE:  {mean_absolute_error(y_test, predictions):.4f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, predictions)):.4f}")
    print(f"R2:   {r2_score(y_test, predictions):.4f}")

    # Build a frontend-friendly product catalogue.
    product_catalog = df[["StockCode", "Description"]].dropna().copy()
    product_catalog["StockCode"] = product_catalog["StockCode"].astype(str)
    product_catalog = (
        product_catalog.groupby("StockCode")["Description"]
        .agg(lambda values: values.mode().iloc[0]
             if not values.mode().empty else values.iloc[0])
        .reset_index()
    )

    # Bundle everything inference needs.
    bundle = {
        "model": model,
        "product_encoder": product_encoder,
        "product_catalog": product_catalog,
        "historical_data": daily,
        "features": FEATURES,
        "last_date": daily["Date"].max()
    }

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    joblib.dump(bundle, args.output, compress=3)
    print(f"\nSaved model bundle to: {args.output}")
    print(f"Products: {len(product_catalog)}")
    print(f"Historical date range: {daily['Date'].min().date()} to "
          f"{daily['Date'].max().date()}")


if __name__ == "__main__":
    main()
