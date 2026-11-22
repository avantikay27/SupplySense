from pathlib import Path
import sys
from functools import lru_cache

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# Project root directory
ROOT_DIR = Path(__file__).resolve().parents[2]

# Ensure project root is available for imports
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from supplysense_ml.forecast import SupplySenseForecaster


router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)


# Load model only once
MODEL_PATH = (
    ROOT_DIR
    / "supplysense_ml"
    / "models"
    / "supplysense_model.pkl"
)


@lru_cache(maxsize=1)
def get_forecaster():
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Trained ML model file not found."
        )

    try:
        return SupplySenseForecaster(MODEL_PATH)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model loading failed: {str(e)}"
        )


class ForecastRequest(BaseModel):
    stock_code: str = Field(..., description="Product StockCode")
    days: int = Field(default=7, ge=1, le=30)


@router.get("/products")
def get_products():
    try:
        forecaster = get_forecaster()

        return {
            "status": "success",
            "total_products": len(forecaster.list_products()),
            "products": forecaster.list_products()
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/")
def generate_forecast(request: ForecastRequest):

    try:
        forecaster = get_forecaster()

        predictions = forecaster.forecast(
            stock_code=request.stock_code,
            days=request.days
        )

        total_demand = sum(
            item["Predicted_Demand"]
            for item in predictions
        )

        return {
            "status": "success",
            "stock_code": request.stock_code,
            "forecast_days": request.days,
            "total_predicted_demand": round(total_demand, 2),
            "forecast": predictions
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecast generation failed: {str(e)}"
        )