import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generation.synthetic_data import SupplyChainDataGenerator
from models.demand_forecasting import DemandForecaster

# Page configuration
st.set_page_config(
    page_title="Supply Chain Optimization Platform",
    page_icon="🚚",
    layout="wide"
)

@st.cache_data
def load_sample_data():
    """Load and cache sample data"""
    generator = SupplyChainDataGenerator()

    data = {
        'products': generator.products,
        'suppliers': generator.suppliers,
        'warehouses': generator.warehouses,
        'stores': generator.stores,
        'sales_data': generator.generate_historical_sales(days=365),
        'supplier_performance': generator.generate_supplier_performance()
    }

    return data, generator

def main():
    """Main dashboard application"""

    # Header
    st.title("🚚 Supply Chain Optimization Platform")
    st.markdown("AI-powered supply chain optimization and analytics")

    # Load data
    with st.spinner('Loading supply chain data...'):
        data, generator = load_sample_data()

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard Overview", "Demand Forecasting", "Data Explorer"]
    )

    if page == "Dashboard Overview":
        st.header("📊 Executive Dashboard")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Products", len(data['products']))
        with col2:
            st.metric("Active Suppliers", len(data['suppliers']))
        with col3:
            st.metric("Warehouses", len(data['warehouses']))
        with col4:
            st.metric("Retail Stores", len(data['stores']))

        # Recent sales trend
        st.subheader("📈 Sales Overview")
        recent_sales = data['sales_data'].tail(1000)
        daily_sales = recent_sales.groupby('date').agg({
            'quantity_sold': 'sum',
            'unit_price': 'mean'
        }).reset_index()

        fig_sales = px.line(daily_sales, x='date', y='quantity_sold', 
                           title='Daily Sales Volume')
        st.plotly_chart(fig_sales, use_container_width=True)

        # Top products
        st.subheader("🏆 Top Selling Products")
        top_products = recent_sales.groupby('product_id')['quantity_sold'].sum().nlargest(10)
        fig_top = px.bar(x=top_products.index, y=top_products.values,
                        title='Top 10 Products by Volume')
        st.plotly_chart(fig_top, use_container_width=True)

    elif page == "Demand Forecasting":
        st.header("📈 Demand Forecasting")

        # Initialize and train forecaster
        with st.spinner('Training demand forecasting models...'):
            forecaster = DemandForecaster()
            forecaster.fit(data['sales_data'], data['products'])

        # Forecast parameters
        col1, col2 = st.columns(2)
        with col1:
            forecast_horizon = st.slider("Forecast Horizon (days)", 7, 90, 30)
        with col2:
            selected_products = st.multiselect(
                "Select Products",
                data['products']['product_id'].tolist(),
                default=data['products']['product_id'].head(5).tolist()
            )

        if st.button("Generate Forecast"):
            with st.spinner('Generating forecasts...'):
                forecast_results = forecaster.get_forecast_summary(
                    selected_products, forecast_horizon
                )

                if not forecast_results.empty:
                    st.subheader("📊 Forecast Results")
                    st.dataframe(forecast_results)

                    # Visualization
                    fig_forecast = px.bar(
                        forecast_results, 
                        x='product_id', 
                        y='avg_daily_demand',
                        title='Average Daily Demand Forecast'
                    )
                    st.plotly_chart(fig_forecast, use_container_width=True)
                else:
                    st.warning("No forecast data available for selected products.")

    elif page == "Data Explorer":
        st.header("🔍 Data Explorer")

        # Data overview
        st.subheader("📦 Products")
        st.dataframe(data['products'].head(10))

        st.subheader("🏪 Suppliers")
        st.dataframe(data['suppliers'].head(10))

        st.subheader("💰 Recent Sales")
        st.dataframe(data['sales_data'].head(20))

        # Product category analysis
        st.subheader("📊 Product Category Distribution")
        category_dist = data['products']['category'].value_counts()
        fig_category = px.pie(values=category_dist.values, names=category_dist.index,
                             title='Products by Category')
        st.plotly_chart(fig_category, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Supply Chain Optimization Platform** - Built with Streamlit and advanced ML algorithms"
    )

if __name__ == "__main__":
    main()
