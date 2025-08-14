import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Tuple, List, Dict
import json

fake = Faker()
np.random.seed(42)
random.seed(42)

class SupplyChainDataGenerator:
    def __init__(self):
        self.products = self._generate_products()
        self.suppliers = self._generate_suppliers()
        self.warehouses = self._generate_warehouses()
        self.stores = self._generate_stores()
        
    def _generate_products(self, n_products: int = 50) -> pd.DataFrame:
        """Generate product catalog"""
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
        
        # Fixed product names - simple approach
        product_names = [
            'Wireless Headphones', 'Smart Watch', 'Laptop Computer', 'Coffee Maker', 'Running Shoes',
            'Winter Jacket', 'Garden Tools', 'Basketball', 'Programming Book', 'Smartphone',
            'Tablet Device', 'Kitchen Blender', 'Yoga Mat', 'Office Chair', 'Desk Lamp',
            'Bluetooth Speaker', 'Fitness Tracker', 'Cooking Pan', 'Tennis Racket', 'Art Supplies',
            'Gaming Mouse', 'Water Bottle', 'Hiking Boots', 'Backpack', 'Phone Charger',
            'Wireless Keyboard', 'Monitor Stand', 'Travel Mug', 'Exercise Bike', 'Reading Light',
            'Portable Battery', 'Camping Tent', 'Soccer Ball', 'Notebook Set', 'Desk Organizer',
            'Wireless Earbuds', 'Smart TV', 'Air Purifier', 'Kitchen Scale', 'Dumbbell Set',
            'Rain Jacket', 'Garden Hose', 'Volleyball', 'Technical Manual', 'Tablet Stand',
            'Gaming Headset', 'Espresso Machine', 'Yoga Block', 'Office Supplies', 'Floor Lamp'
        ]
        
        products = []
        for i in range(n_products):
            products.append({
                'product_id': f'P{i+1:03d}',
                'product_name': product_names[i % len(product_names)] + f' Model {i+1}',
                'category': random.choice(categories),
                'unit_cost': round(random.uniform(5, 500), 2),
                'weight_kg': round(random.uniform(0.1, 50), 2),
                'dimensions_cm': f"{random.randint(5,50)}x{random.randint(5,50)}x{random.randint(5,50)}",
                'seasonality_factor': random.uniform(0.5, 2.0),
                'demand_variability': random.uniform(0.1, 0.8)
            })
        
        return pd.DataFrame(products)
    
    def _generate_suppliers(self, n_suppliers: int = 15) -> pd.DataFrame:
        """Generate supplier information"""
        countries = ['USA', 'China', 'Germany', 'Japan', 'India', 'Mexico']
        
        suppliers = []
        for i in range(n_suppliers):
            suppliers.append({
                'supplier_id': f'S{i+1:03d}',
                'supplier_name': fake.company(),
                'country': random.choice(countries),
                'reliability_score': round(random.uniform(0.7, 0.98), 3),
                'lead_time_days': random.randint(5, 45),
                'lead_time_variability': random.uniform(0.1, 0.5),
                'min_order_quantity': random.randint(50, 1000),
                'quality_score': round(random.uniform(0.8, 0.99), 3),
                'payment_terms_days': random.choice([30, 45, 60, 90])
            })
        
        return pd.DataFrame(suppliers)
    
    def _generate_warehouses(self, n_warehouses: int = 8) -> pd.DataFrame:
        """Generate warehouse locations"""
        cities = [
            ('New York', 40.7128, -74.0060),
            ('Los Angeles', 34.0522, -118.2437),
            ('Chicago', 41.8781, -87.6298),
            ('Houston', 29.7604, -95.3698),
            ('Phoenix', 33.4484, -112.0740),
            ('Philadelphia', 39.9526, -75.1652),
            ('San Antonio', 29.4241, -98.4936),
            ('San Diego', 32.7157, -117.1611)
        ]
        
        warehouses = []
        for i, (city, lat, lon) in enumerate(cities[:n_warehouses]):
            warehouses.append({
                'warehouse_id': f'W{i+1:03d}',
                'city': city,
                'latitude': lat,
                'longitude': lon,
                'capacity_units': random.randint(10000, 50000),
                'operating_cost_per_unit': round(random.uniform(0.5, 2.0), 2),
                'processing_time_hours': random.randint(2, 24)
            })
        
        return pd.DataFrame(warehouses)
    
    def _generate_stores(self, n_stores: int = 25) -> pd.DataFrame:
        """Generate retail store locations"""
        stores = []
        for i in range(n_stores):
            stores.append({
                'store_id': f'ST{i+1:03d}',
                'store_name': f"{fake.city()} Store",
                'latitude': round(fake.latitude(), 4),
                'longitude': round(fake.longitude(), 4),
                'store_type': random.choice(['Flagship', 'Standard', 'Express']),
                'square_footage': random.randint(1000, 10000),
                'customer_traffic_daily': random.randint(100, 2000)
            })
        
        return pd.DataFrame(stores)
    
    def generate_historical_sales(self, days: int = 730) -> pd.DataFrame:
        """Generate historical sales data"""
        start_date = datetime.now() - timedelta(days=days)
        sales_data = []
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Weekend and seasonal effects
            weekend_factor = 1.3 if current_date.weekday() >= 5 else 1.0
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * day / 365.25)
            
            # Generate sales for random subset of products and stores
            n_transactions = random.randint(50, 200)
            
            for _ in range(n_transactions):
                product = self.products.sample(1).iloc[0]
                store = self.stores.sample(1).iloc[0]
                
                base_demand = random.randint(1, 20)
                adjusted_demand = int(base_demand * weekend_factor * 
                                   seasonal_factor * product['seasonality_factor'])
                
                # Fixed: Use random.random() instead of random.choice with p parameter
                promotion_applied = random.random() < 0.15  # 15% chance of promotion
                
                sales_data.append({
                    'date': current_date.date(),
                    'product_id': product['product_id'],
                    'store_id': store['store_id'],
                    'quantity_sold': max(1, adjusted_demand),
                    'unit_price': round(product['unit_cost'] * random.uniform(1.2, 2.5), 2),
                    'promotion_applied': promotion_applied
                })
        
        return pd.DataFrame(sales_data)
    
    def generate_supplier_performance(self, days: int = 365) -> pd.DataFrame:
        """Generate supplier performance history"""
        start_date = datetime.now() - timedelta(days=days)
        performance_data = []
        
        for supplier_idx, supplier in self.suppliers.iterrows():
            # Generate monthly performance records
            for month in range(0, days, 30):
                current_date = start_date + timedelta(days=month)
                
                base_reliability = supplier['reliability_score']
                monthly_variation = np.random.normal(0, 0.05)
                actual_reliability = max(0.5, min(1.0, base_reliability + monthly_variation))
                
                performance_data.append({
                    'date': current_date.date(),
                    'supplier_id': supplier['supplier_id'],
                    'on_time_delivery_rate': round(actual_reliability, 3),
                    'quality_score': round(max(0.7, supplier['quality_score'] + 
                                             np.random.normal(0, 0.02)), 3),
                    'lead_time_actual': max(1, int(supplier['lead_time_days'] + 
                                                 np.random.normal(0, supplier['lead_time_variability'] * 5))),
                    'orders_fulfilled': random.randint(10, 100),
                    'total_order_value': round(random.uniform(10000, 500000), 2)
                })
        
        return pd.DataFrame(performance_data)
    
    def save_all_data(self, output_dir: str = "data/sample/"):
        """Save all generated data to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save master data
        self.products.to_csv(f"{output_dir}/products.csv", index=False)
        self.suppliers.to_csv(f"{output_dir}/suppliers.csv", index=False)
        self.warehouses.to_csv(f"{output_dir}/warehouses.csv", index=False)
        self.stores.to_csv(f"{output_dir}/stores.csv", index=False)
        
        # Generate and save transactional data
        print("🔄 Generating historical sales data...")
        sales_data = self.generate_historical_sales()
        sales_data.to_csv(f"{output_dir}/historical_sales.csv", index=False)
        
        print("🔄 Generating supplier performance data...")
        supplier_performance = self.generate_supplier_performance()
        supplier_performance.to_csv(f"{output_dir}/supplier_performance.csv", index=False)
        
        print(f"✅ Generated sample data saved to {output_dir}")
        print(f"📊 Products: {len(self.products)}")
        print(f"🏪 Suppliers: {len(self.suppliers)}")
        print(f"🏭 Warehouses: {len(self.warehouses)}")
        print(f"🏬 Stores: {len(self.stores)}")
        print(f"💰 Sales records: {len(sales_data)}")
        print(f"📈 Supplier performance records: {len(supplier_performance)}")

if __name__ == "__main__":
    print("🚚 Starting Supply Chain Data Generation...")
    generator = SupplyChainDataGenerator()
    generator.save_all_data()
    print("🎉 Data generation complete!")