
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SupplySense API",
    description="Smart Demand and Supply Prediction System",
    version="1.0.0"
)

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
