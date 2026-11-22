"""
SupplySense inference module.

Loads the exported model bundle and generates recursive multi-day forecasts
for a selected StockCode.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd


class SupplySenseForecaster:
    def __init__(self, model_path):
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.product_encoder = bundle["product_encoder"]
        self.product_catalog = bundle["product_catalog"].copy()
        self.historical_data = bundle["historical_data"].copy()
        self.features = bundle["features"]
        self.last_date = pd.Timestamp(bundle["last_date"])

        self.historical_data["StockCode"] = (
            self.historical_data["StockCode"].astype(str)
        )

    def list_products(self):
        """Return product codes and descriptions for a frontend dropdown."""
        return self.product_catalog.sort_values("Description").to_dict(
            orient="records"
        )

    def forecast(self, stock_code, days=7):
        """
        Forecast demand recursively for one product.

        Each predicted day is appended to the history used to calculate
        the next day's lag and rolling-average features.
        """
        stock_code = str(stock_code)

        if days < 1 or days > 30:
            raise ValueError("days must be between 1 and 30")

        known_codes = set(self.product_encoder.classes_.astype(str))
        if stock_code not in known_codes:
            raise ValueError(f"Unknown StockCode: {stock_code}")

        history_rows = self.historical_data[
            self.historical_data["StockCode"] == stock_code
        ].sort_values("Date")

        history = history_rows["Demand"].astype(float).tolist()
        if len(history) < 14:
            raise ValueError(
                f"Insufficient history for StockCode {stock_code}; "
                "at least 14 daily observations are required."
            )

        product_id = int(self.product_encoder.transform([stock_code])[0])
        forecast_dates = pd.date_range(
            start=self.last_date + pd.Timedelta(days=1),
            periods=days,
            freq="D"
        )

        results = []
        for forecast_date in forecast_dates:
            row = pd.DataFrame([{
                "Product_ID": product_id,
                "Month": forecast_date.month,
                "DayOfWeek": forecast_date.dayofweek,
                "Lag1": history[-1],
                "Lag7": history[-7],
                "Roll7": float(np.mean(history[-7:])),
                "Roll14": float(np.mean(history[-14:]))
            }])[self.features]

            prediction = float(self.model.predict(row)[0])
            prediction = max(0.0, prediction)

            results.append({
                "Date": forecast_date.date().isoformat(),
                "StockCode": stock_code,
                "Predicted_Demand": round(prediction, 2)
            })
            history.append(prediction)

        return results


if __name__ == "__main__":
    # Example local test:
    forecaster = SupplySenseForecaster(
        Path("models") / "supplysense_model.pkl"
    )
    print(forecaster.forecast("85123A", days=7))
