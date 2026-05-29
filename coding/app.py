"""
Main Streamlit application for Sales Data Analysis System.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

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
