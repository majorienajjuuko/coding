"""
Report generation module.
"""

import pandas as pd
from datetime import datetime

def generate_summary_report(data, date_range=None):
    """
    Generate a text summary report.
    """
    sales = data['sales']
    dealers = data['dealers']
    car_models = data['car_models']
    recalls = data['recalls']
    
    total_revenue = sales['Profit'].sum()
    total_units = sales['Quantity Sold'].sum()
    avg_profit_per_unit = sales['Avg_Profit_Per_Unit'].mean()
    
    top_model = sales.groupby('Model')['Profit'].sum().idxmax()
    top_model_revenue = sales.groupby('Model')['Profit'].sum().max()
    
    top_dealer = sales.groupby('Dealer ID')['Profit'].sum().idxmax()
    top_dealer_revenue = sales.groupby('Dealer ID')['Profit'].sum().max()
    
    report = f"""
    ========================================
    SALES PERFORMANCE SUMMARY REPORT
    ========================================
    
    Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    OVERALL METRICS:
    ----------------
    Total Revenue: ${total_revenue:,.2f}
    Total Units Sold: {total_units:,.0f}
    Average Profit per Unit: ${avg_profit_per_unit:,.2f}
    Number of Models: {sales['Model'].nunique()}
    Number of Dealers: {dealers['Dealer ID'].nunique() if not dealers.empty else 0}
    Number of Recalls: {len(recalls):,}
    
    TOP PERFORMERS:
    ----------------
    Best Performing Model: {top_model} (${top_model_revenue:,.2f})
    Best Performing Dealer: {top_dealer} (${top_dealer_revenue:,.2f})
    
    DATE RANGE:
    ----------------
    Start Date: {sales['Date'].min().strftime('%Y-%m-%d')}
    End Date: {sales['Date'].max().strftime('%Y-%m-%d')}
    """
    
    return report

def generate_model_performance_report(model_performance):
    """
    Generate report on model performance.
    """
    if model_performance.empty:
        return "No model performance data available."
    
    report = "\n    MODEL PERFORMANCE REPORT\n    " + "=" * 40 + "\n\n"
    
    for idx, row in model_performance.iterrows():
        report += f"""
    Model: {row['Model']}
      - Total Profit: ${row['Profit']:,.2f}
      - Total Units Sold: {row['Quantity Sold']:,.0f}
      - Avg Profit/Unit: ${row['Avg_Profit_Per_Unit']:,.2f}
      - Number of Dealers: {row['Num_Dealers']}
      - Profit per Dealer: ${row['Profit_Per_Dealer']:,.2f}
    """
    
    return report

def generate_dealer_performance_report(dealer_performance):
    """
    Generate report on dealer performance.
    """
    if dealer_performance.empty:
        return "No dealer performance data available."
    
    report = "\n    DEALER PERFORMANCE REPORT\n    " + "=" * 40 + "\n\n"
    
    for idx, row in dealer_performance.iterrows():
        dealer_name = row.get('Dealer Name', f"Dealer {row['Dealer ID']}")
        report += f"""
    {dealer_name} (ID: {row['Dealer ID']})
      - Location: {row.get('City', 'N/A')}, {row.get('State', 'N/A')}
      - Total Profit: ${row['Profit']:,.2f}
      - Total Units Sold: {row['Quantity Sold']:,.0f}
    """
    
    return report

def generate_recalls_report(recalls_impact):
    """
    Generate report on recalls impact.
    """
    if recalls_impact.empty:
        return "No recall data available."
    
    report = "\n    RECALLS IMPACT REPORT\n    " + "=" * 40 + "\n\n"
    
    for idx, row in recalls_impact.head(10).iterrows():
        recall_ratio = row['Recall_Ratio']
        impact_level = "HIGH" if recall_ratio > 0.1 else "MEDIUM" if recall_ratio > 0.05 else "LOW"
        
        report += f"""
    Model: {row['Model']}
      - Recall Units: {row['Recall_Units']:,.0f}
      - Total Sales: {row['Quantity Sold']:,.0f}
      - Recall Ratio: {recall_ratio:.1%}
      - Impact Level: {impact_level}
    """
    
    return report

def export_to_excel(data, filename=None):
    """
    Export analysis data to Excel file.
    """
    if filename is None:
        filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        data['sales'].to_excel(writer, sheet_name='Sales Data', index=False)
        
        if not data.get('model_performance', pd.DataFrame()).empty:
            data['model_performance'].to_excel(writer, sheet_name='Model Performance', index=False)
        
        if not data.get('dealer_performance', pd.DataFrame()).empty:
            data['dealer_performance'].to_excel(writer, sheet_name='Dealer Performance', index=False)
        
        if not data.get('monthly_trends', pd.DataFrame()).empty:
            data['monthly_trends'].to_excel(writer, sheet_name='Monthly Trends', index=False)
        
        if not data.get('yearly_summary', pd.DataFrame()).empty:
            data['yearly_summary'].to_excel(writer, sheet_name='Yearly Summary', index=False)
    
    return filename
