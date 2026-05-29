"""
Main Streamlit application for Sales Data Analysis System.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
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

# Page configuration
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

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_sales' not in st.session_state:
    st.session_state.filtered_sales = None

@st.cache_data
def load_data():
    """Load and cache data."""
    return load_and_process_data(data_dir="data")

def apply_filters(sales_df, year_range, models, dealers):
    """Apply filters to sales data."""
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
    st.markdown('<div class="main-header">Sales Data Analysis System</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        try:
            data = load_data()
            st.session_state.data = data
            
            # Merge with dealers for enriched data
            sales_with_dealers = merge_with_dealers(data['sales'], data['dealers'])
            data['sales_with_dealers'] = sales_with_dealers
            
            # Prepare recalls data
            data['recalls_processed'] = prepare_recalls_data(data['recalls'])
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Please ensure all data files are in the 'data' directory.")
            st.info("Required files: AU_Sales_By_Model.xlsx, car_models.xlsx, Car_Recalls.xlsx, dealers.xlsx, sales_by_model.xlsx")
            return
    
    sales_df = data['sales']
    dealers_df = data['dealers']
    recalls_df = data['recalls_processed']
    
    if sales_df.empty:
        st.error("No sales data found. Please check your data files.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Year filter
    years = sorted(sales_df['Year'].unique())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years)),
        step=1
    )
    
    # Model filter
    all_models = ['All'] + sorted(sales_df['Model'].unique().tolist())
    selected_models = st.sidebar.multiselect(
        "Model",
        options=all_models,
        default=['All']
    )
    
    # Dealer filter
    all_dealers = ['All'] + sorted(sales_df['Dealer ID'].unique().tolist())
    selected_dealers = st.sidebar.multiselect(
        "Dealer",
        options=all_dealers,
        default=['All']
    )
    
    # Apply filters
    filtered_sales = apply_filters(sales_df, year_range, selected_models, selected_dealers)
    
    # Check if filtered data is empty
    if filtered_sales.empty:
        st.warning("No data matches the selected filters. Please adjust your filter criteria.")
        return
    
    # Summary metrics
    st.header("📈 Key Metrics")
    
    total_revenue = filtered_sales['Profit'].sum()
    total_units = filtered_sales['Quantity Sold'].sum()
    avg_profit_per_unit = filtered_sales['Avg_Profit_Per_Unit'].mean()
    unique_models = filtered_sales['Model'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("Total Units Sold", f"{total_units:,.0f}")
    with col3:
        st.metric("Avg Profit/Unit", f"${avg_profit_per_unit:,.2f}")
    with col4:
        st.metric("Models Sold", unique_models)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Trends", "🏆 Top Performers", "📅 Seasonality", 
        "📋 Model Analysis", "📍 Dealer Analysis", "⚠️ Recalls Impact"
    ])
    
    with tab1:
        st.subheader("Sales Trends Over Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_trends = get_monthly_trends(filtered_sales)
            if not monthly_trends.empty:
                profit_chart = create_profit_trend_chart(monthly_trends)
                st.plotly_chart(profit_chart, use_container_width=True)
            else:
                st.info("No monthly trend data available")
        
        with col2:
            monthly_trends = get_monthly_trends(filtered_sales)
            if not monthly_trends.empty:
                quantity_chart = create_quantity_trend_chart(monthly_trends)
                st.plotly_chart(quantity_chart, use_container_width=True)
            else:
                st.info("No monthly trend data available")
        
        # Yearly summary and growth
        yearly_summary = get_yearly_summary(filtered_sales)
        if not yearly_summary.empty:
            try:
                growth_chart = create_yearly_growth_chart(yearly_summary)
                st.plotly_chart(growth_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create growth chart: {e}")
            
            # Yearly summary table
            st.subheader("Yearly Summary")
            try:
                st.dataframe(
                    yearly_summary.style.format({
                        'Profit': '${:,.2f}',
                        'Quantity Sold': '{:,.0f}',
                        'Avg_Profit_Per_Unit': '${:,.2f}',
                        'Profit_Growth': '{:.1f}%',
                        'Units_Growth': '{:.1f}%'
                    }),
                    use_container_width=True
                )
            except Exception as e:
                st.dataframe(yearly_summary, use_container_width=True)
        
        # Quarterly breakdown
        quarterly_data = get_quarterly_breakdown(filtered_sales)
        if not quarterly_data.empty:
            quarterly_chart = create_quarterly_breakdown_chart(quarterly_data)
            st.plotly_chart(quarterly_chart, use_container_width=True)
    
    with tab2:
        st.subheader("Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            metric_choice = st.selectbox("Metric for Top Models", ["Profit", "Quantity"], key="models_metric")
            top_models = get_top_models(filtered_sales, metric=metric_choice, n=10)
            if not top_models.empty:
                models_chart = create_top_models_bar_chart(top_models, metric=metric_choice)
                st.plotly_chart(models_chart, use_container_width=True)
                
                # Model share pie chart
                share_chart = create_model_share_pie_chart(top_models)
                st.plotly_chart(share_chart, use_container_width=True)
            else:
                st.info("No model data available")
        
        with col2:
            dealer_metric = st.selectbox("Metric for Top Dealers", ["Profit", "Quantity"], key="dealers_metric")
            top_dealers = get_top_dealers(filtered_sales, metric=dealer_metric, n=10)
            if not top_dealers.empty:
                dealers_chart = create_top_dealers_chart(top_dealers, metric=dealer_metric)
                st.plotly_chart(dealers_chart, use_container_width=True)
            else:
                st.info("No dealer data available")
        
        # Top models over time
        ranking_over_time = get_model_ranking_over_time(filtered_sales, n_models=5)
        if not ranking_over_time.empty:
            st.subheader("Top Models Performance Over Time")
            top_models_trend = create_top_models_over_time_chart(ranking_over_time)
            st.plotly_chart(top_models_trend, use_container_width=True)
    
    with tab3:
        st.subheader("Seasonal Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            seasonal_data = get_seasonal_analysis(filtered_sales)
            if not seasonal_data.empty:
                try:
                    st.dataframe(
                        seasonal_data.style.format({
                            'Profit': '${:,.2f}',
                            'Quantity Sold': '{:,.0f}'
                        }),
                        use_container_width=True
                    )
                except Exception as e:
                    st.dataframe(seasonal_data, use_container_width=True)
            else:
                st.info("No seasonal data available")
        
        with col2:
            try:
                heatmap = create_seasonal_heatmap(filtered_sales)
                st.plotly_chart(heatmap, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create heatmap: {e}")
    
    with tab4:
        st.subheader("Model Performance Analysis")
        
        model_performance = get_model_performance(filtered_sales)
        
        if not model_performance.empty:
            try:
                comparison_chart = create_model_comparison_chart(model_performance)
                st.plotly_chart(comparison_chart, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create comparison chart: {e}")
            
            # Detailed model performance table
            st.subheader("Detailed Model Performance")
            try:
                st.dataframe(
                    model_performance.style.format({
                        'Profit': '${:,.2f}',
                        'Quantity Sold': '{:,.0f}',
                        'Avg_Profit_Per_Unit': '${:,.2f}',
                        'Profit_Per_Dealer': '${:,.2f}',
                        'Units_Per_Dealer': '{:,.1f}'
                    }),
                    use_container_width=True
                )
            except Exception as e:
                st.dataframe(model_performance, use_container_width=True)
            
            # Generate and display model report
            if st.button("Generate Model Performance Report"):
                report = generate_model_performance_report(model_performance)
                st.text(report)
    
    with tab5:
        st.subheader("Dealer Analysis")
        
        dealer_performance = get_dealer_performance_with_details(filtered_sales, dealers_df)
        
        if not dealer_performance.empty:
            # Dealer map
            try:
                dealer_map = create_dealer_map(dealer_performance)
                st.plotly_chart(dealer_map, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create dealer map: {e}")
            
            # Dealer performance table
            st.subheader("Dealer Performance Details")
            display_cols = ['Dealer ID', 'Dealer Name', 'City', 'State', 'Profit', 'Quantity Sold']
            available_cols = [c for c in display_cols if c in dealer_performance.columns]
            
            try:
                st.dataframe(
                    dealer_performance[available_cols].style.format({
                        'Profit': '${:,.2f}',
                        'Quantity Sold': '{:,.0f}'
                    }),
                    use_container_width=True
                )
            except Exception as e:
                st.dataframe(dealer_performance[available_cols], use_container_width=True)
            
            # Generate dealer report
            if st.button("Generate Dealer Performance Report"):
                report = generate_dealer_performance_report(dealer_performance)
                st.text(report)
    
    with tab6:
        st.subheader("Recalls Impact Analysis")
        
        if not recalls_df.empty:
            recalls_impact = get_recalls_impact(recalls_df, filtered_sales)
            
            if not recalls_impact.empty:
                try:
                    impact_chart = create_recalls_impact_chart(recalls_impact)
                    st.plotly_chart(impact_chart, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create impact chart: {e}")
                
                # Detailed recall impact table
                st.subheader("Detailed Recall Impact by Model")
                display_cols = ['Model', 'Profit', 'Quantity Sold', 'Recall_Units', 'Recall_Ratio']
                available_cols = [c for c in display_cols if c in recalls_impact.columns]
                
                try:
                    st.dataframe(
                        recalls_impact[available_cols].style.format({
                            'Profit': '${:,.2f}',
                            'Quantity Sold': '{:,.0f}',
                            'Recall_Units': '{:,.0f}',
                            'Recall_Ratio': '{:.1%}'
                        }),
                        use_container_width=True
                    )
                except Exception as e:
                    st.dataframe(recalls_impact[available_cols], use_container_width=True)
                
                # Generate recalls report
                if st.button("Generate Recalls Impact Report"):
                    report = generate_recalls_report(recalls_impact)
                    st.text(report)
            else:
                st.info("No recall impact data available for the selected filters.")
        else:
            st.info("No recall data available.")
    
    # Sidebar - Export section
    st.sidebar.markdown("---")
    st.sidebar.header("📁 Export Data")
    
    export_data = {
        'sales': filtered_sales,
        'model_performance': get_model_performance(filtered_sales),
        'dealer_performance': get_dealer_performance_with_details(filtered_sales, dealers_df),
        'monthly_trends': get_monthly_trends(filtered_sales),
        'yearly_summary': get_yearly_summary(filtered_sales)
    }
    
    if st.sidebar.button("Export to Excel"):
        try:
            filename = export_to_excel(export_data)
            with open(filename, 'rb') as f:
                st.sidebar.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.sidebar.error(f"Export failed: {e}")
    
    # Sidebar - Summary Report
    st.sidebar.markdown("---")
    st.sidebar.header("📄 Generate Report")
    
    if st.sidebar.button("Generate Summary Report"):
        summary = get_data_summary(data)
        report = generate_summary_report(data)
        st.sidebar.text_area("Report", report, height=300)

if __name__ == "__main__":
    main()
