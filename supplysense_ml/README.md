# SupplySense – Machine Learning Module

This folder contains the machine-learning contribution for SupplySense:
training, evaluation, model export, and reusable product-level forecasting.

## Folder structure

```text
supplysense_ml/
├── models/
│   └── supplysense_model.pkl   # Add the exported model bundle here
├── train_model.py              # Reproducible preprocessing and training
├── forecast.py                # Reusable forecasting class
├── requirements.txt
├── evaluation_report.md
└── README.md
```

## Dataset

The model was developed using the Kaggle Online Retail dataset
(`data.csv`). The CSV is not included in this folder. Obtain it from the
project's approved dataset source and place it at the path used below.

The training script expects these columns:
`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`,
and `UnitPrice`.

## Train the model

From this folder, install dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python train_model.py --data data.csv --output models/supplysense_model.pkl
```

The script:
1. Removes cancelled invoices and rows with non-positive quantity or price.
2. Parses invoice dates and aggregates quantity by product and day.
3. Fills missing product-day combinations with zero demand.
4. Creates calendar, lag, and rolling-average features.
5. Splits data chronologically (80% earlier dates for training, 20% later dates for testing).
6. Trains a shared Random Forest regression model.
7. Prints test metrics and exports the model bundle.

## Generate a seven-day forecast

Place the exported `supplysense_model.pkl` inside `models/`, then:

```python
from forecast import SupplySenseForecaster

forecaster = SupplySenseForecaster("models/supplysense_model.pkl")

# Populate a product dropdown:
products = forecaster.list_products()

# Forecast one selected product:
result = forecaster.forecast("85123A", days=7)
print(result)
```

`forecast()` returns a list of dictionaries containing `Date`, `StockCode`,
and `Predicted_Demand`. The function supports 1–30 forecast days.

## FastAPI integration example

Your backend teammate can load the forecaster once when the API starts:

```python
from forecast import SupplySenseForecaster

forecaster = SupplySenseForecaster("models/supplysense_model.pkl")

@app.get("/api/products")
def get_products():
    return forecaster.list_products()

@app.get("/api/forecast/{stock_code}")
def get_forecast(stock_code: str):
    return forecaster.forecast(stock_code, days=7)
```

Adapt route names and error handling to the existing backend. Do not load the
27 MB model separately on every request.

## Important limitations

- The source dataset ends on 2011-12-09. The generated dates therefore begin
  on 2011-12-10. This is a historical demonstration, not a current live-demand
  forecast.
- The seven-day function is recursive: each predicted value is used to build
  the next day's lag and rolling features.
- The printed test metrics are rolling one-step-ahead metrics. Test rows use
  actual lagged demand values from the dataset; they are not equivalent to a
  fixed seven-day recursive forecast.
- Demand spikes are difficult for this model to predict. Review
  `evaluation_report.md` before presenting model performance.
- `Product_ID` is created using LabelEncoder and is treated numerically by
  Random Forest. This is a limitation because product codes are categorical.
- The model is a prototype trained on a historical retail dataset and should
  be retrained on recent, relevant data before real operational use.
