"""
Visualization functions for the sales dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_profit_trend_chart(monthly_trends):
    """
    Create profit trend line chart.
    """
    if monthly_trends.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_trends['Date'],
        y=monthly_trends['Profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Monthly Profit Trend',
        xaxis_title='Month',
        yaxis_title='Profit ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_quantity_trend_chart(monthly_trends):
    """
    Create quantity sold trend line chart.
    """
    if monthly_trends.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_trends['Date'],
        y=monthly_trends['Quantity Sold'],
        mode='lines+markers',
        name='Units Sold',
        line=dict(color='#A23B72', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(162, 59, 114, 0.1)'
    ))
    
    fig.update_layout(
        title='Monthly Units Sold Trend',
        xaxis_title='Month',
        yaxis_title='Units Sold',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_top_models_bar_chart(top_models, metric='Profit'):
    """
    Create bar chart for top models.
    """
    if top_models.empty:
        return go.Figure()
    
    metric_label = 'Profit ($)' if metric == 'Profit' else 'Units Sold'
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#048A81'] * (len(top_models) // 5 + 1)
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_models['Model'],
            y=top_models[metric],
            marker_color=colors[:len(top_models)],
            text=top_models[metric].apply(lambda x: f'${x:,.0f}' if metric == 'Profit' else f'{x:,.0f}'),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f'Top Models by {metric}',
        xaxis_title='Model',
        yaxis_title=metric_label,
        template='plotly_white'
    )
    
    return fig

def create_top_dealers_chart(top_dealers, metric='Profit'):
    """
    Create bar chart for top dealers.
    """
    if top_dealers.empty:
        return go.Figure()
    
    metric_label = 'Profit ($)' if metric == 'Profit' else 'Units Sold'
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_dealers['Dealer ID'].astype(str),
            y=top_dealers[metric],
            marker_color='#2E86AB',
            text=top_dealers[metric].apply(lambda x: f'${x:,.0f}' if metric == 'Profit' else f'{x:,.0f}'),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f'Top Dealers by {metric}',
        xaxis_title='Dealer ID',
        yaxis_title=metric_label,
        template='plotly_white'
    )
    
    return fig

def create_seasonal_heatmap(sales_df):
    """
    Create heatmap of sales by month and year.
    """
    if sales_df.empty:
        return go.Figure()
    
    pivot_data = sales_df.pivot_table(
        values='Profit',
        index='Year',
        columns='Month_Name',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    pivot_data = pivot_data[[m for m in month_order if m in pivot_data.columns]]
    
    fig = px.imshow(
        pivot_data,
        text_auto='.0s',
        aspect='auto',
        color_continuous_scale='Viridis',
        title='Seasonal Sales Heatmap (Profit)'
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Year',
        template='plotly_white'
    )
    
    return fig

def create_model_share_pie_chart(top_models, n=6):
    """
    Create pie chart for model market share.
    """
    if top_models.empty:
        return go.Figure()
    
    top_n = top_models.head(n).copy()
    other_sum = top_models.iloc[n:]['Profit'].sum() if len(top_models) > n else 0
    
    if other_sum > 0:
        other_row = pd.DataFrame({'Model': ['Other'], 'Profit': [other_sum]})
        top_n = pd.concat([top_n, other_row], ignore_index=True)
    
    fig = px.pie(
        top_n,
        values='Profit',
        names='Model',
        title='Profit Distribution by Model',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(template='plotly_white')
    
    return fig

def create_model_comparison_chart(model_performance):
    """
    Create comparison chart for model performance metrics.
    """
    if model_performance.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Profit by Model', 'Units Sold by Model'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Profit bar chart
    fig.add_trace(
        go.Bar(
            x=model_performance['Model'],
            y=model_performance['Profit'],
            name='Profit',
            marker_color='#2E86AB',
            text=model_performance['Profit'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Units bar chart
    fig.add_trace(
        go.Bar(
            x=model_performance['Model'],
            y=model_performance['Quantity Sold'],
            name='Units Sold',
            marker_color='#F18F01',
            text=model_performance['Quantity Sold'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Model Performance Comparison',
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_top_models_over_time_chart(ranking_over_time):
    """
    Create line chart showing top models' performance over time.
    """
    if ranking_over_time.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#048A81']
    
    for i, model in enumerate(ranking_over_time['Model'].unique()):
        model_data = ranking_over_time[ranking_over_time['Model'] == model]
        fig.add_trace(go.Scatter(
            x=model_data['Date'],
            y=model_data['Profit'],
            mode='lines+markers',
            name=model,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title='Top Models Profit Over Time',
        xaxis_title='Date',
        yaxis_title='Profit ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_quarterly_breakdown_chart(quarterly_data):
    """
    Create bar chart for quarterly breakdown.
    """
    if quarterly_data.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Quarterly Profit', 'Quarterly Units Sold'),
        vertical_spacing=0.15
    )
    
    # Profit chart
    fig.add_trace(
        go.Bar(
            x=quarterly_data['Year_Quarter'],
            y=quarterly_data['Profit'],
            name='Profit',
            marker_color='#2E86AB',
            text=quarterly_data['Profit'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Units chart
    fig.add_trace(
        go.Bar(
            x=quarterly_data['Year_Quarter'],
            y=quarterly_data['Quantity Sold'],
            name='Units Sold',
            marker_color='#A23B72',
            text=quarterly_data['Quantity Sold'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title='Quarterly Sales Breakdown',
        height=600,
        template='plotly_white',
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_dealer_map(dealer_performance):
    """
    Create map visualization for dealer locations.
    """
    if dealer_performance.empty or 'Latitude' not in dealer_performance.columns:
        return go.Figure()
    
    # Filter out rows with missing coordinates
    map_data = dealer_performance.dropna(subset=['Latitude', 'Longitude'])
    
    if map_data.empty:
        return go.Figure()
    
    fig = px.scatter_geo(
        map_data,
        lat='Latitude',
        lon='Longitude',
        size='Profit',
        hover_name='Dealer Name',
        hover_data={
            'City': True,
            'State': True,
            'Profit': ':$,.0f',
            'Quantity Sold': ':,.0f'
        },
        title='Dealer Locations and Performance',
        projection='albers usa',
        size_max=50,
        color='Profit',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        title_x=0.5,
        geo=dict(
            scope='usa',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)'
        ),
        template='plotly_white'
    )
    
    return fig

def create_recalls_impact_chart(recalls_impact):
    """
    Create chart showing recall impact on models.
    """
    if recalls_impact.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Recall Ratio by Model', 'Recall Units vs Total Sales'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Recall ratio chart
    fig.add_trace(
        go.Bar(
            x=recalls_impact['Model'].head(10),
            y=recalls_impact['Recall_Ratio'].head(10),
            name='Recall Ratio',
            marker_color='#C73E1D',
            text=recalls_impact['Recall_Ratio'].head(10).apply(lambda x: f'{x:.1%}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Recall vs Sales chart (using a subset)
    comparison_data = recalls_impact.head(10).copy()
    
    fig.add_trace(
        go.Bar(
            x=comparison_data['Model'],
            y=comparison_data['Recall_Units'],
            name='Recall Units',
            marker_color='#F18F01'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=comparison_data['Model'],
            y=comparison_data['Quantity Sold'],
            name='Total Sales',
            marker_color='#2E86AB'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Recall Impact Analysis',
        height=500,
        template='plotly_white',
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_yearly_growth_chart(yearly_summary):
    """
    Create chart showing year-over-year growth.
    """
    if yearly_summary.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Year-over-Year Profit Growth', 'Year-over-Year Units Growth'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Profit growth
    fig.add_trace(
        go.Bar(
            x=yearly_summary['Year'].astype(str),
            y=yearly_summary['Profit_Growth'].fillna(0),
            name='Profit Growth %',
            marker_color='#2E86AB',
            text=yearly_summary['Profit_Growth'].fillna(0).apply(lambda x: f'{x:.1f}%'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Units growth
    fig.add_trace(
        go.Bar(
            x=yearly_summary['Year'].astype(str),
            y=yearly_summary['Units_Growth'].fillna(0),
            name='Units Growth %',
            marker_color='#A23B72',
            text=yearly_summary['Units_Growth'].fillna(0).apply(lambda x: f'{x:.1f}%'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title='Year-over-Year Growth',
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    return fig
