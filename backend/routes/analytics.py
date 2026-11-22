
from fastapi import APIRouter, HTTPException
from services.data_service import load_data
from services.analytics_service import (
    get_overview,
    get_daily_demand,
    create_product_features
)

router = APIRouter()

@router.get("/analytics/overview")
def analytics_overview():
    try:
        df = load_data()
        return get_overview(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/daily-demand")
def daily_demand():
    try:
        df = load_data()
        result = get_daily_demand(df)
        result["date"] = result["date"].astype(str)
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
def get_products():
    try:
        df = load_data()

        products = (
            df[["StockCode", "Description"]]
            .dropna(subset=["StockCode"])
            .drop_duplicates(subset=["StockCode"])
            .sort_values("StockCode")
        )

        return {
            "total_products": len(products),
            "products": products.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{stock_code}/demand")
def product_demand(stock_code: str):
    try:
        df = load_data()

        product_df = df[
            df["StockCode"].astype(str) == stock_code
        ].copy()

        if product_df.empty:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        product_df["date"] = product_df["InvoiceDate"].dt.normalize()

        demand = (
            product_df.groupby("date")["Quantity"]
            .sum()
            .reset_index()
            .sort_values("date")
        )

        demand["date"] = demand["date"].astype(str)

        return {
            "stock_code": stock_code,
            "product_name": product_df["Description"].iloc[0],
            "daily_demand": demand.to_dict(orient="records")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/products/{stock_code}/features")
def product_features(stock_code: str):
    try:
        df = load_data()

        features = create_product_features(df)

        product_features_df = features[
            features["StockCode"].astype(str) == stock_code
        ]

        if product_features_df.empty:
            raise HTTPException(
                status_code=404,
                detail="Product features not found"
            )

        product_features_df = product_features_df.copy()
        product_features_df["date"] = (
            product_features_df["date"].astype(str)
        )

        return {
            "stock_code": stock_code,
            "total_records": len(product_features_df),
            "features": product_features_df.to_dict(orient="records")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))