from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import uvicorn
from datetime import datetime
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.demand_forecasting import DemandForecaster
from data_generation.synthetic_data import SupplyChainDataGenerator

app = FastAPI(
    title="Supply Chain Optimization Platform API",
    description="AI-powered supply chain optimization and analytics",
    version="1.0.0"
)

# Global data store
data_store = {}
demand_forecaster = DemandForecaster()

class ForecastRequest(BaseModel):
    product_ids: List[str]
    forecast_horizon: int = Field(default=30, ge=1, le=365)

@app.on_event("startup")
async def startup_event():
    """Initialize the application with sample data"""
    global data_store

    # Generate sample data
    generator = SupplyChainDataGenerator()

    data_store['products'] = generator.products
    data_store['suppliers'] = generator.suppliers
    data_store['warehouses'] = generator.warehouses
    data_store['stores'] = generator.stores
    data_store['sales_data'] = generator.generate_historical_sales(days=365)

    # Train models
    demand_forecaster.fit(data_store['sales_data'], data_store['products'])

    print("✅ API initialized with sample data and trained models")

@app.get("/")
async def root():
    return {
        "message": "Supply Chain Optimization Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": {"demand_forecaster": demand_forecaster.is_fitted},
        "data_loaded": {
            "products": len(data_store.get('products', [])),
            "suppliers": len(data_store.get('suppliers', [])),
            "sales_records": len(data_store.get('sales_data', []))
        }
    }

@app.get("/products")
async def get_products():
    """Get all products"""
    return data_store['products'].to_dict('records')

@app.post("/forecast/demand")
async def forecast_demand(request: ForecastRequest):
    """Generate demand forecast for specified products"""
    try:
        forecast_summary = demand_forecaster.get_forecast_summary(
            request.product_ids, 
            request.forecast_horizon
        )

        return {
            "forecast_horizon_days": request.forecast_horizon,
            "products_count": len(request.product_ids),
            "forecasts": forecast_summary.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
