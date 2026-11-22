
import math

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from routes.forecast import get_forecaster

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)

class InventoryRequest(BaseModel):
    stock_code: str = Field(..., description="Product StockCode")
    current_stock: float = Field(..., ge=0)
    lead_time_days: int = Field(default=7, ge=1, le=30)
    safety_stock_days: int = Field(default=3, ge=0, le=30)

@router.post("/recommendation")
def inventory_recommendation(request: InventoryRequest):
    try:
        total_days = (
            request.lead_time_days + request.safety_stock_days
        )

        if total_days > 30:
            raise HTTPException(
                status_code=400,
                detail="Lead time plus safety stock days cannot exceed 30."
            )

        forecaster = get_forecaster()

        predictions = forecaster.forecast(
            stock_code=request.stock_code,
            days=total_days
        )

        lead_time_demand = sum(
            item["Predicted_Demand"]
            for item in predictions[:request.lead_time_days]
        )

        safety_stock = sum(
            item["Predicted_Demand"]
            for item in predictions[request.lead_time_days:]
        )

        reorder_point = lead_time_demand + safety_stock

        recommended_order = math.ceil(
            max(0, reorder_point - request.current_stock)
        )

        status = (
            "REORDER"
            if request.current_stock <= reorder_point
            else "SUFFICIENT_STOCK"
        )

        product_name = next(
            (
                item.get("Description", "Unknown")
                for item in forecaster.list_products()
                if str(item.get("StockCode")) == request.stock_code
            ),
            "Unknown"
        )

        return {
            "status": "success",
            "stock_code": request.stock_code,
            "product_name": product_name,
            "current_stock": request.current_stock,
            "lead_time_days": request.lead_time_days,
            "safety_stock_days": request.safety_stock_days,
            "forecast_lead_time_demand": round(lead_time_demand, 2),
            "calculated_safety_stock": round(safety_stock, 2),
            "reorder_point": round(reorder_point, 2),
            "inventory_status": status,
            "recommended_order_quantity": recommended_order,
            "forecast": predictions
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inventory recommendation failed: {str(e)}"
        )