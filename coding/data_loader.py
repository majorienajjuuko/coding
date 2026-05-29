"""
Simplified data loading module.
"""

import pandas as pd
import os

def load_and_process_data(data_dir="data"):
    """Load and process all data files."""
    
    data = {
        'sales': pd.DataFrame(),
        'car_models': pd.DataFrame(),
        'recalls': pd.DataFrame(),
        'dealers': pd.DataFrame()
    }
    
    # Define file paths
    files = {
        'sales_by_model': 'AU_Sales_By_Model.xlsx',
        'car_models': 'car_models.xlsx',
        'recalls': 'Car_Recalls.xlsx',
        'dealers': 'dealers.xlsx',
        'additional_sales': 'sales_by_model.xlsx'
    }
    
    sales_dfs = []
    
    for key, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_excel(filepath)
                print(f"✅ Loaded {filename}: {len(df)} rows")
                
                if key in ['sales_by_model', 'additional_sales']:
                    # Check if it has the expected columns
                    expected_cols = ['Year', 'Month', 'Date', 'Model', 'Dealer ID', 'Quantity Sold', 'Profit']
                    if all(col in df.columns for col in expected_cols):
                        sales_dfs.append(df[expected_cols])
                    else:
                        print(f"   Skipping - unexpected columns: {df.columns.tolist()}")
                elif key == 'car_models':
                    data['car_models'] = df
                elif key == 'recalls':
                    data['recalls'] = df
                elif key == 'dealers':
                    data['dealers'] = df
                    
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    # Combine sales data
    if sales_dfs:
        combined_sales = pd.concat(sales_dfs, ignore_index=True)
        
        # Clean data
        combined_sales['Year'] = combined_sales['Year'].astype(int)
        combined_sales['Date'] = pd.to_datetime(combined_sales['Date'])
        combined_sales['Quantity Sold'] = pd.to_numeric(combined_sales['Quantity Sold'], errors='coerce')
        combined_sales['Profit'] = pd.to_numeric(combined_sales['Profit'], errors='coerce')
        
        # Remove NaN rows
        combined_sales = combined_sales.dropna(subset=['Quantity Sold', 'Profit'])
        
        # Add derived columns
        combined_sales['Avg_Profit_Per_Unit'] = combined_sales['Profit'] / combined_sales['Quantity Sold']
        combined_sales['Month_Num'] = combined_sales['Date'].dt.month
        combined_sales['Quarter'] = combined_sales['Date'].dt.quarter
        combined_sales['Year_Month'] = combined_sales['Date'].dt.strftime('%Y-%m')
        
        data['sales'] = combined_sales
        print(f"✅ Total sales records: {len(combined_sales)}")
    else:
        print("❌ No sales data files found")
    
    return data

def merge_with_dealers(sales_df, dealers_df):
    """Merge sales with dealer info."""
    if sales_df.empty or dealers_df.empty:
        return sales_df
    
    try:
        merged = sales_df.merge(
            dealers_df[['Dealer ID', 'Country', 'State', 'City', 'Dealer Name']],
            on='Dealer ID',
            how='left'
        )
        return merged
    except Exception as e:
        print(f"Error merging dealers: {e}")
        return sales_df

def prepare_recalls_data(recalls_df):
    """Prepare recalls data."""
    if recalls_df.empty:
        return recalls_df
    
    try:
        df = recalls_df.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        df['Units'] = pd.to_numeric(df['Units'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error preparing recalls: {e}")
        return recalls_df

def get_data_summary(data):
    """Get data summary."""
    sales = data.get('sales', pd.DataFrame())
    
    if sales.empty:
        return {}
    
    return {
        'total_revenue': sales['Profit'].sum(),
        'total_units': sales['Quantity Sold'].sum(),
        'unique_models': sales['Model'].nunique(),
        'unique_dealers': sales['Dealer ID'].nunique()
    }
