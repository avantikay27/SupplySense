
from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import date, timedelta

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)

class ForecastRequest(BaseModel):
    days: int = Field(default=7, ge=1, le=30)

@router.post("/")
def generate_forecast(request: ForecastRequest):

    forecast = []

    base_demand = 15000

    for i in range(1, request.days + 1):
        forecast_date = date.today() + timedelta(days=i)

        predicted_demand = base_demand + (i * 250)

        forecast.append({
            "date": forecast_date.isoformat(),
            "predicted_demand": predicted_demand
        })

    return {
        "status": "success",
        "forecast_days": request.days,
        "forecast": forecast
    }