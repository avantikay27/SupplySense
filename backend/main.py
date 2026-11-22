from routes.forecast import router as forecast_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analytics import router as analytics_router
from routes.inventory import router as inventory_router
app = FastAPI(
    title="SupplySense API",
    description="Smart Demand and Supply Prediction System",
    version="1.0.0"
)
app.include_router(analytics_router)
app.include_router(forecast_router)
app.include_router(inventory_router)
# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "message": "Welcome to SupplySense API",
        "status": "Backend is running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": "SupplySense"
    }
