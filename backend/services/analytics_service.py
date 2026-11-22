import pandas as pd


def get_overview(df):

    # Calculate total revenue
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    overview = {
        "total_records": len(df),
        "total_revenue": round(df["Revenue"].sum(), 2),
        "total_products": df["StockCode"].nunique(),
        "total_customers": df["CustomerID"].nunique(),
        "total_countries": df["Country"].nunique()
    }

    return overview
def get_daily_demand(df):

    # Remove cancelled invoices
    df = df[
        ~df["InvoiceNo"].astype(str).str.startswith("C")
    ]

    # Remove invalid transactions
    df = df[
        (df["Quantity"] > 0) &
        (df["UnitPrice"] > 0)
    ]

    

    # Extract date
    df["date"] = df["InvoiceDate"].dt.normalize()

    # Calculate daily demand
    daily_demand = (
        df.groupby("date")["Quantity"]
        .sum()
        .reset_index()
    )

    daily_demand.columns = ["date", "sales"]

    # Sort dates
    daily_demand = daily_demand.sort_values("date")

    return daily_demand

def create_features(df):

    df = df.copy()

    # Extract day of week
    df["day_of_week"] = df["date"].dt.dayofweek

    # Extract month
    df["month"] = df["date"].dt.month

    # Previous 7 days demand
    df["lag_7"] = df["sales"].shift(7)

    # Average demand of previous 7 days
    df["rolling_mean_7"] = (
        df["sales"].shift(1).rolling(window=7).mean()
    )

    # Remove missing values
    df = df.dropna()

    return df
def create_product_features(df):

    df = df.copy()

    # Remove invalid transactions
    df = df[
        (df["Quantity"] > 0) &
        (df["UnitPrice"] > 0)
    ]

    # Group demand by product and date
    df["date"] = df["InvoiceDate"].dt.normalize()

    daily = (
        df.groupby(["StockCode", "date"])["Quantity"]
        .sum()
        .reset_index()
        .sort_values(["StockCode", "date"])
    )

    # Create product-wise features
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["month"] = daily["date"].dt.month

    daily["lag_7"] = (
        daily.groupby("StockCode")["Quantity"].shift(7)
    )

    daily["rolling_mean_7"] = (
        daily.groupby("StockCode")["Quantity"]
        .transform(lambda x: x.shift(1).rolling(7).mean())
    )

    daily = daily.dropna()

    return daily
def create_product_features(df):

    df = df.copy()

    # Remove cancelled and invalid transactions
    df = df[
        (~df["InvoiceNo"].astype(str).str.startswith("C")) &
        (df["Quantity"] > 0) &
        (df["UnitPrice"] > 0)
    ].copy()

    # Extract date
    df["date"] = df["InvoiceDate"].dt.normalize()

    # Aggregate demand product-wise
    daily = (
        df.groupby(["StockCode", "date"])["Quantity"]
        .sum()
        .reset_index()
        .sort_values(["StockCode", "date"])
    )

    daily.rename(columns={"Quantity": "sales"}, inplace=True)

    # Create product-wise features
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["month"] = daily["date"].dt.month

    daily["lag_7"] = (
        daily.groupby("StockCode")["sales"].shift(7)
    )

    daily["rolling_mean_7"] = (
        daily.groupby("StockCode")["sales"]
        .transform(lambda x: x.shift(1).rolling(7).mean())
    )

    daily = daily.dropna().reset_index(drop=True)

    return daily