"""
Main Streamlit application for Sales Data Analysis System.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import sys
import traceback

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Sales Analysis System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Try to import modules with error handling
try:
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from data_loader import load_and_process_data, merge_with_dealers, prepare_recalls_data, get_data_summary
    from analysis import (
        get_top_models, get_top_dealers, get_monthly_trends, get_yearly_summary,
        get_model_performance, get_seasonal_analysis, get_recalls_impact,
        get_dealer_performance_with_details, get_model_ranking_over_time,
        get_quarterly_breakdown
    )
    from visualizations import (
        create_profit_trend_chart, create_quantity_trend_chart,
        create_top_models_bar_chart, create_top_dealers_chart,
        create_seasonal_heatmap, create_model_share_pie_chart,
        create_model_comparison_chart, create_top_models_over_time_chart,
        create_quarterly_breakdown_chart, create_dealer_map,
        create_recalls_impact_chart, create_yearly_growth_chart
    )
    from reports import (
        generate_summary_report, generate_model_performance_report,
        generate_dealer_performance_report, generate_recalls_report,
        export_to_excel
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    IMPORT_SUCCESS = False
    st.error(f"❌ Import Error: {e}")
    st.code(traceback.format_exc())
    st.info(f"Current directory: {current_dir}")
    st.info(f"Files in directory: {os.listdir(current_dir) if os.path.exists(current_dir) else 'N/A'}")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_sales' not in st.session_state:
    st.session_state.filtered_sales = None

@st.cache_data(ttl=3600)
def load_cached_data():
    """Load and cache data."""
    # Try multiple possible data directories
    possible_data_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
        "/mount/src/coding/data",
        "/mount/src/coding/coding/data",
        "./data",
        "../data"
    ]
    
    for data_dir in possible_data_dirs:
        if os.path.exists(data_dir):
            try:
                print(f"Trying data directory: {data_dir}")
                data = load_and_process_data(data_dir=data_dir)
                if data and not data.get('sales', pd.DataFrame()).empty:
                    print(f"✅ Data loaded from: {data_dir}")
                    return data
            except Exception as e:
                print(f"Failed to load from {data_dir}: {e}")
                continue
    
    print("Could not find data files")
    return None

def apply_filters(sales_df, year_range, models, dealers):
    """Apply filters to sales data."""
    if sales_df.empty:
        return sales_df
    
    filtered = sales_df.copy()
    
    if year_range and len(year_range) == 2:
        filtered = filtered[(filtered['Year'] >= year_range[0]) & (filtered['Year'] <= year_range[1])]
    
    if models and 'All' not in models:
        filtered = filtered[filtered['Model'].isin(models)]
    
    if dealers and 'All' not in dealers:
        filtered = filtered[filtered['Dealer ID'].isin(dealers)]
    
    return filtered

def main():
    """Main application entry point."""
    
    # Header
    st.markdown('<div class="main-header">🚗 Sales Data Analysis System</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check if imports worked
    if not IMPORT_SUCCESS:
        st.error("Failed to import required modules. Please check the files exist.")
        return
    
    # Load data
    with st.spinner("📂 Loading data..."):
        try:
            data = load_cached_data()
            
            if data is None or data.get('sales', pd.DataFrame()).empty:
                st.error("❌ No sales data found. Please check your data files.")
                st.info("Required files in 'data' folder:")
                st.code("""
                data/
                ├── AU_Sales_By_Model.xlsx
                ├── car_models.xlsx
                ├── Car_Recalls.xlsx
                ├── dealers.xlsx
                └── sales_by_model.xlsx
                """)
                
                # Show what directories exist
                for check_dir in ["./data", "../data", "/mount/src/coding/data", "/mount/src/coding/coding/data"]:
                    if os.path.exists(check_dir):
                        st.write(f"📁 Files in {check_dir}:")
                        for f in os.listdir(check_dir):
                            st.write(f"   - {f}")
                return
            
            st.session_state.data = data
            st.success("✅ Data loaded successfully!")
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.code(traceback.format_exc())
            return
    
    sales_df = data['sales']
    dealers_df = data['dealers']
    
    if sales_df.empty:
        st.error("No sales data available.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("---")
    
    # Year filter
    years = sorted(sales_df['Year'].unique())
    if len(years) > 1:
        year_range = st.sidebar.slider(
            "📅 Year Range",
            min_value=int(min(years)),
            max_value=int(max(years)),
            value=(int(min(years)), int(max(years))),
            step=1
        )
    else:
        year_range = (int(years[0]), int(years[0]))
        st.sidebar.info(f"Only {years[0]} data available")
    
    # Model filter
    all_models = ['All'] + sorted(sales_df['Model'].unique().tolist())
    selected_models = st.sidebar.multiselect(
        "🚗 Model",
        options=all_models,
        default=['All']
    )
    
    # Apply filters
    filtered_sales = apply_filters(sales_df, year_range, selected_models, [])
    
    # Check if filtered data is empty
    if filtered_sales.empty:
        st.warning("⚠️ No data matches the selected filters. Please adjust your filter criteria.")
        return
    
    # Display metrics
    st.header("📈 Key Metrics")
    
    total_revenue = filtered_sales['Profit'].sum()
    total_units = filtered_sales['Quantity Sold'].sum()
    unique_models = filtered_sales['Model'].nunique()
    unique_dealers = filtered_sales['Dealer ID'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("📦 Total Units Sold", f"{total_units:,.0f}")
    with col3:
        st.metric("🚗 Models Sold", unique_models)
    with col4:
        st.metric("🏪 Dealers", unique_dealers)
    
    st.markdown("---")
    
    # Simple tabs for demonstration
    tab1, tab2, tab3 = st.tabs(["📊 Trends", "🏆 Top Models", "📋 Data Table"])
    
    with tab1:
        st.subheader("Monthly Sales Trends")
        
        monthly = filtered_sales.groupby(filtered_sales['Date'].dt.to_period('M')).agg({
            'Profit': 'sum',
            'Quantity Sold': 'sum'
        }).reset_index()
        monthly['Date'] = monthly['Date'].astype(str)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.line_chart(monthly.set_index('Date')['Profit'])
            st.caption("Monthly Profit Trend")
        
        with col2:
            st.line_chart(monthly.set_index('Date')['Quantity Sold'])
            st.caption("Monthly Units Sold Trend")
    
    with tab2:
        st.subheader("Top Performing Models")
        
        top_models = filtered_sales.groupby('Model')['Profit'].sum().sort_values(ascending=False).head(10)
        
        st.bar_chart(top_models)
        st.caption("Top 10 Models by Profit")
        
        # Show data table
        st.subheader("All Models Performance")
        model_summary = filtered_sales.groupby('Model').agg({
            'Profit': 'sum',
            'Quantity Sold': 'sum'
        }).sort_values('Profit', ascending=False).reset_index()
        
        model_summary['Profit'] = model_summary['Profit'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(model_summary, use_container_width=True)
    
    with tab3:
        st.subheader("Sales Data")
        st.dataframe(filtered_sales.head(100), use_container_width=True)
        
        # Download button
        csv = filtered_sales.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        "📌 **About**\n\n"
        "This dashboard analyzes automotive sales data.\n\n"
        f"📅 Data from {sales_df['Date'].min().strftime('%Y-%m')} to {sales_df['Date'].max().strftime('%Y-%m')}\n\n"
        f"🚗 {sales_df['Model'].nunique()} models\n\n"
        f"🏪 {dealers_df['Dealer ID'].nunique() if not dealers_df.empty else 0} dealers"
    )

if __name__ == "__main__":
    main()
