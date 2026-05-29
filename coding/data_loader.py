"""
Data loading and processing module for the sales analysis system.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_all_data(data_dir="data"):
    """
    Load all Excel files from the data directory.
    """
    data = {}
    
    files = {
        'sales_by_model': 'AU_Sales_By_Model.xlsx',
        'car_models': 'car_models.xlsx',
        'recalls': 'Car_Recalls.xlsx',
        'dealers': 'dealers.xlsx',
        'additional_sales': 'sales_by_model.xlsx'
    }
    
    for key, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                data[key] = pd.read_excel(filepath)
                print(f"Loaded {key}: {len(data[key])} rows")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                data[key] = pd.DataFrame()
        else:
            print(f"File not found: {filepath}")
            data[key] = pd.DataFrame()
    
    return data

def combine_sales_data(sales_by_model, additional_sales):
    """
    Combine sales data from both files.
    """
    if sales_by_model.empty and additional_sales.empty:
        return pd.DataFrame()
    
    # Standardize column names
    sales_dfs = []
    
    for df, name in [(sales_by_model, 'main'), (additional_sales, 'additional')]:
        if not df.empty:
            # Ensure consistent column names
            expected_cols = ['Year', 'Month', 'Date', 'Model', 'Dealer ID', 'Quantity Sold', 'Profit']
            if all(col in df.columns for col in expected_cols):
                sales_dfs.append(df[expected_cols].copy())
    
    if not sales_dfs:
        return pd.DataFrame()
    
    combined = pd.concat(sales_dfs, ignore_index=True)
    
    # Clean and convert data types
    combined['Year'] = combined['Year'].astype(int)
    combined['Date'] = pd.to_datetime(combined['Date'])
    combined['Quantity Sold'] = combined['Quantity Sold'].astype(float)
    combined['Profit'] = combined['Profit'].astype(float)
    
    # Remove duplicates if any
    combined = combined.drop_duplicates()
    
    return combined

def process_sales_data(combined_sales):
    """
    Process and enrich sales data with additional metrics.
    """
    if combined_sales.empty:
        return combined_sales
    
    df = combined_sales.copy()
    
    # Add derived columns
    df['Month_Num'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    df['Year_Month'] = df['Date'].dt.strftime('%Y-%m')
    df['Year_Quarter'] = df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str)
    
    # Calculate average profit per unit
    df['Avg_Profit_Per_Unit'] = df['Profit'] / df['Quantity Sold']
    
    # Add date components for filtering
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    
    return df

def load_and_process_data(data_dir="data"):
    """
    Main function to load and process all data.
    """
    print("Loading data...")
    raw_data = load_all_data(data_dir)
    
    print("Combining sales data...")
    combined_sales = combine_sales_data(
        raw_data.get('sales_by_model', pd.DataFrame()),
        raw_data.get('additional_sales', pd.DataFrame())
    )
    
    print("Processing sales data...")
    processed_sales = process_sales_data(combined_sales)
    
    print(f"Total sales records: {len(processed_sales)}")
    print(f"Date range: {processed_sales['Date'].min()} to {processed_sales['Date'].max()}")
    
    return {
        'sales': processed_sales,
        'car_models': raw_data.get('car_models', pd.DataFrame()),
        'recalls': raw_data.get('recalls', pd.DataFrame()),
        'dealers': raw_data.get('dealers', pd.DataFrame())
    }

def merge_with_dealers(sales_df, dealers_df):
    """
    Merge sales data with dealer information.
    """
    if sales_df.empty or dealers_df.empty:
        return sales_df
    
    merged = sales_df.merge(
        dealers_df[['Dealer ID', 'Country', 'State', 'City', 'Dealer Name', 'Latitude', 'Longitude']],
        on='Dealer ID',
        how='left'
    )
    
    return merged

def merge_with_car_models(sales_df, car_models_df):
    """
    Merge sales data with car model IDs.
    """
    if sales_df.empty or car_models_df.empty:
        return sales_df
    
    merged = sales_df.merge(
        car_models_df,
        left_on='Model',
        right_on='Model',
        how='left'
    )
    
    return merged

def prepare_recalls_data(recalls_df):
    """
    Prepare and clean recalls data.
    """
    if recalls_df.empty:
        return recalls_df
    
    df = recalls_df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    return df

def get_data_summary(data):
    """
    Generate summary statistics for the dashboard.
    """
    sales = data['sales']
    dealers = data['dealers']
    recalls = data['recalls']
    
    summary = {
        'total_revenue': float(sales['Profit'].sum()) if not sales.empty else 0,
        'total_units': int(sales['Quantity Sold'].sum()) if not sales.empty else 0,
        'avg_profit_per_unit': float(sales['Avg_Profit_Per_Unit'].mean()) if not sales.empty else 0,
        'unique_models': int(sales['Model'].nunique()) if not sales.empty else 0,
        'unique_dealers': int(dealers['Dealer ID'].nunique()) if not dealers.empty else 0,
        'total_recalls': int(len(recalls)) if not recalls.empty else 0,
        'date_range': {
            'start': sales['Date'].min().strftime('%Y-%m-%d') if not sales.empty else 'N/A',
            'end': sales['Date'].max().strftime('%Y-%m-%d') if not sales.empty else 'N/A'
        }
    }
    
    return summary
