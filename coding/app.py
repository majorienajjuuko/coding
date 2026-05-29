# Add at the top of each function in analysis.py
def get_top_models(sales_df, metric='Profit', n=10):
    if sales_df.empty:
        return pd.DataFrame()
    # ... rest of function

def get_top_dealers(sales_df, metric='Profit', n=10):
    if sales_df.empty:
        return pd.DataFrame()
    # ... rest of function

def get_monthly_trends(sales_df):
    if sales_df.empty:
        return pd.DataFrame()
    # ... rest of function

# Add similar checks to all functions
