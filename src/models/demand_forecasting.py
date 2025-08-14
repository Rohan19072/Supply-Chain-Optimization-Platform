import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

class DemandForecaster:
    def __init__(self):
        self.prophet_models = {}
        self.rf_models = {}
        self.is_fitted = False

    def prepare_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare sales data for forecasting"""
        # Convert date column
        sales_data['date'] = pd.to_datetime(sales_data['date'])

        # Aggregate daily sales by product
        daily_sales = sales_data.groupby(['date', 'product_id']).agg({
            'quantity_sold': 'sum',
            'unit_price': 'mean',
            'promotion_applied': 'any'
        }).reset_index()

        # Add time-based features
        daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
        daily_sales['month'] = daily_sales['date'].dt.month
        daily_sales['quarter'] = daily_sales['date'].dt.quarter
        daily_sales['is_weekend'] = daily_sales['day_of_week'].isin([5, 6]).astype(int)

        return daily_sales

    def create_prophet_features(self, data: pd.DataFrame, product_id: str) -> pd.DataFrame:
        """Create Prophet-compatible dataset for a specific product"""
        product_data = data[data['product_id'] == product_id].copy()

        # Prophet requires 'ds' and 'y' columns
        prophet_data = pd.DataFrame({
            'ds': product_data['date'],
            'y': product_data['quantity_sold']
        })

        # Add regressors
        prophet_data['promotion'] = product_data['promotion_applied'].astype(int)
        prophet_data['is_weekend'] = product_data['is_weekend']

        return prophet_data.sort_values('ds')

    def fit_prophet_model(self, data: pd.DataFrame, product_id: str):
        """Fit Prophet model for a specific product"""
        prophet_data = self.create_prophet_features(data, product_id)

        if len(prophet_data) < 30:  # Need sufficient data
            return None

        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )

        # Add regressors
        model.add_regressor('promotion')
        model.add_regressor('is_weekend')

        try:
            model.fit(prophet_data)
            return model
        except:
            return None

    def fit(self, sales_data: pd.DataFrame, products: pd.DataFrame):
        """Fit forecasting models for all products"""
        prepared_data = self.prepare_data(sales_data)

        print("🔄 Training demand forecasting models...")

        for product_id in products['product_id'].unique():
            print(f"   Training models for {product_id}")

            # Fit Prophet model
            prophet_model = self.fit_prophet_model(prepared_data, product_id)
            if prophet_model:
                self.prophet_models[product_id] = prophet_model

        self.is_fitted = True
        print(f"✅ Trained models for {len(self.prophet_models)} products")

    def predict_prophet(self, product_id: str, days_ahead: int = 30) -> pd.DataFrame:
        """Generate Prophet predictions"""
        if product_id not in self.prophet_models:
            return pd.DataFrame()

        model = self.prophet_models[product_id]

        # Create future dataframe
        future = model.make_future_dataframe(periods=days_ahead)

        # Add regressor values for future dates
        future['promotion'] = 0  # Assume no promotions
        future['is_weekend'] = future['ds'].dt.dayofweek.isin([5, 6]).astype(int)

        forecast = model.predict(future)

        # Return only future predictions
        return forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def get_forecast_summary(self, product_ids: list, days_ahead: int = 30) -> pd.DataFrame:
        """Get forecast summary for multiple products"""
        summaries = []

        for product_id in product_ids:
            if product_id in self.prophet_models:
                prophet_pred = self.predict_prophet(product_id, days_ahead)
                if not prophet_pred.empty:
                    avg_demand = prophet_pred['yhat'].mean()
                    total_demand = prophet_pred['yhat'].sum()

                    summaries.append({
                        'product_id': product_id,
                        'avg_daily_demand': round(max(0, avg_demand), 2),
                        'total_demand_forecast': round(max(0, total_demand), 2),
                        'forecast_period_days': days_ahead
                    })

        return pd.DataFrame(summaries)
