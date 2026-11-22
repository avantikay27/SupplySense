# SupplySense – Smart Demand & Supply Prediction

SupplySense is a machine-learning-based demand forecasting project designed to predict product-level demand and help support better inventory planning.

## Project Structure

```text
SupplySense/
├── backend/          # FastAPI backend
├── supplysense_ml/   # Machine learning module
├── README.md         # Main project documentation
└── .gitignore
```

## Machine Learning

The ML module uses the Kaggle Online Retail dataset to train a shared Random Forest regression model.

Key capabilities:
- Product-level demand prediction.
- Seven-day demand forecasting.
- Historical demand feature engineering.
- Model evaluation and performance reporting.

See [`supplysense_ml/README.md`](supplysense_ml/README.md) for training instructions, forecasting usage, dependencies, and limitations.

## Backend Integration

The FastAPI backend provides endpoints for:
- Retrieving available products.
- Generating forecasts for a selected product.

## Dataset

The project uses the [Kaggle Online Retail dataset](https://www.kaggle.com/datasets/carrie1/ecommerce-data).

The dataset is not included in this repository.

## Current Status

SupplySense is a prototype. Its ML model was trained on historical retail data ending December 9, 2011. Forecasts are demonstrations and should not be treated as current operational demand predictions.
