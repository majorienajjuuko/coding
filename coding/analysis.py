"""
Analysis functions for sales data.
"""

import pandas as pd
import numpy as np

def get_top_models(sales_df, metric='Profit', n=10):
    """
    Get top N models by profit or quantity.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    if metric == 'Profit':
        result = sales_df.groupby('Model')['Profit'].sum().sort_values(ascending=False).head(n)
    elif metric == 'Quantity':
        result = sales_df.groupby('Model')['Quantity Sold'].sum().sort_values(ascending=False).head(n)
    else:
        result = sales_df.groupby('Model')[metric].sum().sort_values(ascending=False).head(n)
    
    return result.reset_index()

def get_top_dealers(sales_df, metric='Profit', n=10):
    """
    Get top N dealers by profit or quantity.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    if metric == 'Profit':
        result = sales_df.groupby('Dealer ID')['Profit'].sum().sort_values(ascending=False).head(n)
    elif metric == 'Quantity':
        result = sales_df.groupby('Dealer ID')['Quantity Sold'].sum().sort_values(ascending=False).head(n)
    else:
        result = sales_df.groupby('Dealer ID')[metric].sum().sort_values(ascending=False).head(n)
    
    return result.reset_index()

def get_monthly_trends(sales_df):
    """
    Calculate monthly sales trends.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    monthly = sales_df.groupby(['Year', 'Month_Num', 'Month_Name']).agg({
        'Profit': 'sum',
        'Quantity Sold': 'sum'
    }).reset_index()
    
    monthly['Date'] = pd.to_datetime(monthly['Year'].astype(str) + '-' + monthly['Month_Num'].astype(str) + '-01')
    monthly = monthly.sort_values('Date')
    
    return monthly

def get_yearly_summary(sales_df):
    """
    Get yearly summary statistics.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    yearly = sales_df.groupby('Year').agg({
        'Profit': 'sum',
        'Quantity Sold': 'sum',
        'Avg_Profit_Per_Unit': 'mean'
    }).reset_index()
    
    yearly['Profit_Growth'] = yearly['Profit'].pct_change() * 100
    yearly['Units_Growth'] = yearly['Quantity Sold'].pct_change() * 100
    
    return yearly

def get_model_performance(sales_df):
    """
    Analyze performance by model.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    performance = sales_df.groupby('Model').agg({
        'Profit': 'sum',
        'Quantity Sold': 'sum',
        'Avg_Profit_Per_Unit': 'mean',
        'Dealer ID': 'nunique'
    }).rename(columns={'Dealer ID': 'Num_Dealers'}).reset_index()
    
    performance['Profit_Per_Dealer'] = performance['Profit'] / performance['Num_Dealers']
    performance['Units_Per_Dealer'] = performance['Quantity Sold'] / performance['Num_Dealers']
    
    return performance.sort_values('Profit', ascending=False)

def get_seasonal_analysis(sales_df):
    """
    Analyze seasonal patterns by month.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    seasonal = sales_df.groupby('Month_Name').agg({
        'Profit': 'mean',
        'Quantity Sold': 'mean'
    }).reset_index()
    
    # Order months correctly
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    seasonal['Month_Order'] = seasonal['Month_Name'].apply(lambda x: month_order.index(x) if x in month_order else 0)
    seasonal = seasonal.sort_values('Month_Order')
    
    return seasonal

def get_recalls_impact(recalls_df, sales_df):
    """
    Analyze potential impact of recalls on sales.
    """
    if recalls_df.empty or sales_df.empty:
        return pd.DataFrame()
    
    recall_by_model = recalls_df.groupby('Model').agg({
        'Units': 'sum',
        'System_Affected': lambda x: list(x)
    }).reset_index()
    
    # Merge with sales performance
    model_performance = get_model_performance(sales_df)
    
    impact_analysis = model_performance.merge(
        recall_by_model,
        on='Model',
        how='left'
    )
    
    impact_analysis['Recall_Units'] = impact_analysis['Units'].fillna(0)
    impact_analysis['Recall_Ratio'] = impact_analysis['Recall_Units'] / impact_analysis['Quantity Sold']
    impact_analysis['Recall_Ratio'] = impact_analysis['Recall_Ratio'].fillna(0)
    
    return impact_analysis.sort_values('Recall_Ratio', ascending=False)

def get_dealer_performance_with_details(sales_df, dealers_df):
    """
    Get detailed dealer performance including location data.
    """
    if sales_df.empty or dealers_df.empty:
        return pd.DataFrame()
    
    sales_by_dealer = sales_df.groupby('Dealer ID').agg({
        'Profit': 'sum',
        'Quantity Sold': 'sum'
    }).reset_index()
    
    result = sales_by_dealer.merge(
        dealers_df[['Dealer ID', 'Dealer Name', 'City', 'State', 'Country', 'Latitude', 'Longitude']],
        on='Dealer ID',
        how='left'
    )
    
    return result

def get_model_ranking_over_time(sales_df, n_models=5):
    """
    Track top models' performance over time.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    # Get top N models overall
    top_models = sales_df.groupby('Model')['Profit'].sum().nlargest(n_models).index.tolist()
    
    # Filter and aggregate monthly
    filtered = sales_df[sales_df['Model'].isin(top_models)]
    monthly = filtered.groupby(['Year', 'Month_Num', 'Model'])['Profit'].sum().reset_index()
    monthly['Date'] = pd.to_datetime(monthly['Year'].astype(str) + '-' + monthly['Month_Num'].astype(str) + '-01')
    
    return monthly

def get_quarterly_breakdown(sales_df):
    """
    Get quarterly breakdown of sales.
    """
    if sales_df.empty:
        return pd.DataFrame()
    
    quarterly = sales_df.groupby('Year_Quarter').agg({
        'Profit': 'sum',
        'Quantity Sold': 'sum'
    }).reset_index()
    
    # Extract year and quarter for sorting
    quarterly[['Year', 'Quarter']] = quarterly['Year_Quarter'].str.split('-Q', expand=True)
    quarterly['Year'] = quarterly['Year'].astype(int)
    quarterly['Quarter'] = quarterly['Quarter'].astype(int)
    quarterly = quarterly.sort_values(['Year', 'Quarter'])
    
    return quarterly
