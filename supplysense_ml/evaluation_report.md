# SupplySense – Model Evaluation Report

## Model

- Approach: shared multi-product regression model
- Estimator: `RandomForestRegressor`
- Trees: 100
- Maximum depth: 15
- Minimum samples per leaf: 5
- Random state: 42
- Features: `Product_ID`, `Month`, `DayOfWeek`, `Lag1`, `Lag7`, `Roll7`, `Roll14`
- Product count: 3,922
- Daily history: 374 calendar days, 2010-12-01 to 2011-12-09

## Data preparation

Cancelled invoices were removed. Rows with non-positive quantity or unit
price were excluded. Quantity was aggregated by StockCode and calendar date.
Missing product-date combinations were filled with zero demand.

The chronological split used the first 80% of unique dates for training and
the final 20% for testing.

## Recorded evaluation results

These are the results recorded during the project notebook experiments.

### Shared model – all product-days

| Metric | Result |
|---|---:|
| MAE | 6.2964 |
| RMSE | 155.5216 |
| R² | 0.0082 |

The low overall MAE is influenced by the large number of low- and zero-demand
product-days. The much larger RMSE indicates substantial errors on high-demand
days. R² close to zero indicates weak explanatory performance overall.

### Shared model – product 85123A

| Metric | Result |
|---|---:|
| MAE | 79.6627 |
| RMSE | 161.2397 |
| R² | 0.0586 |
| Actual average demand | 105.625 |
| Predicted average demand | 102.6878 |

For comparison, the best recorded single-product Random Forest experiment on
the same test dates had MAE 93.3229, RMSE 172.6370, and R² -0.0792.
The shared model performed better on these recorded metrics for this one
product, but its R² remains low.

## Observed limitations

- The model smooths demand and misses some sharp sales spikes.
- Overall metrics can hide weak performance for individual products.
- The shared model uses a numeric LabelEncoder product ID, although product
  identity is categorical.
- The evaluation is rolling one-step-ahead: test features use actual
  historical demand for lag calculations. This is not the same as evaluating
  a seven-day recursive forecast.
- The dataset is historical and ends on 2011-12-09.

## Interpretation

The project demonstrates a complete multi-product forecasting pipeline and
a working recursive seven-day inference function. It should be presented as
a prototype, not as a proven high-accuracy or live forecasting system.
Further validation, improved categorical product handling, and recent data
are needed before operational deployment.
