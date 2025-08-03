# ===== dash_app/app.py =====
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import numpy as np
from plotly.subplots import make_subplots

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css'
])

# Custom CSS for dark theme
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #0d1421;
                color: #f0f0f0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .dash-container {
                background-color: #0d1421;
            }
            .card {
                background-color: #2b2f36;
                border: 1px solid #2b2f36;
                border-radius: 8px;
                margin-bottom: 1rem;
            }
            .card-header {
                background-color: #1e2329;
                border-bottom: 1px solid #2b2f36;
                padding: 1rem;
                font-weight: bold;
            }
            .metric-card {
                background-color: #2b2f36;
                border: 1px solid #2b2f36;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                margin-bottom: 1rem;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #00d4aa;
            }
            .metric-label {
                color: #848e9c;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Database connection
def get_db_connection():
    conn = sqlite3.connect('../db.sqlite3')
    return conn

# Data fetching functions
def fetch_exchange_rates(timeframe='30d'):
    conn = get_db_connection()
    
    # Calculate date range
    end_date = datetime.now()
    if timeframe == '7d':
        start_date = end_date - timedelta(days=7)
    elif timeframe == '30d':
        start_date = end_date - timedelta(days=30)
    elif timeframe == '90d':
        start_date = end_date - timedelta(days=90)
    elif timeframe == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    query = '''
    SELECT rate, buy_rate, sell_rate, timestamp
    FROM rates_exchangerate
    WHERE timestamp >= ? AND timestamp <= ?
    ORDER BY timestamp
    '''
    
    df = pd.read_sql_query(query, conn, params=[start_date, end_date])
    conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['rate'] = pd.to_numeric(df['rate'])
        df['buy_rate'] = pd.to_numeric(df['buy_rate'])
        df['sell_rate'] = pd.to_numeric(df['sell_rate'])
    
    return df

def calculate_analytics(df):
    if df.empty:
        return {}
    
    current_rate = df.iloc[-1]['rate']
    previous_rate = df.iloc[-2]['rate'] if len(df) > 1 else current_rate
    
    analytics = {
        'current_rate': current_rate,
        'previous_rate': previous_rate,
        'change': current_rate - previous_rate,
        'change_percent': ((current_rate - previous_rate) / previous_rate * 100) if previous_rate != 0 else 0,
        'high': df['rate'].max(),
        'low': df['rate'].min(),
        'avg': df['rate'].mean(),
        'volatility': df['rate'].std(),
        'volume': len(df)  # Number of data points as proxy for volume
    }
    
    return analytics

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("UGX/USD Forex Analytics Dashboard", className="text-center mb-4"),
        html.P("Advanced analytics and visualizations for UGX to USD exchange rates", 
               className="text-center text-muted")
    ], className="container mt-4"),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("Timeframe:", className="form-label"),
            dcc.Dropdown(
                id='timeframe-dropdown',
                options=[
                    {'label': '7 Days', 'value': '7d'},
                    {'label': '30 Days', 'value': '30d'},
                    {'label': '90 Days', 'value': '90d'},
                    {'label': '1 Year', 'value': '1y'}
                ],
                value='30d',
                style={'background-color': '#2b2f36', 'color': '#f0f0f0'}
            )
        ], className="col-md-4"),
        
        html.Div([
            html.Button("Refresh Data", id="refresh-btn", className="btn btn-primary")
        ], className="col-md-4 d-flex align-items-end"),
        
        html.Div([
            html.P(id="last-update", className="text-muted small mt-3")
        ], className="col-md-4")
    ], className="row container"),
    
    # Metrics Cards
    html.Div(id="metrics-cards", className="container mt-4"),
    
    # Charts
    html.Div([
        # Main Rate Chart
        html.Div([
            html.Div("Exchange Rate Trend", className="card-header"),
            dcc.Graph(id="rate-chart")
        ], className="card"),
        
        # Candlestick Chart
        html.Div([
            html.Div("Candlestick Chart (OHLC)", className="card-header"),
            dcc.Graph(id="candlestick-chart")
        ], className="card"),
        
        # Spread Analysis
        html.Div([
            html.Div("Buy/Sell Spread Analysis", className="card-header"),
            dcc.Graph(id="spread-chart")
        ], className="card"),
        
        # Volatility Chart
        html.Div([
            html.Div("Rate Volatility", className="card-header"),
            dcc.Graph(id="volatility-chart")
        ], className="card")
    ], className="container"),
    
    # Auto-refresh component
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
], className="dash-container")

# Callbacks
@callback(
    [Output('metrics-cards', 'children'),
     Output('rate-chart', 'figure'),
     Output('candlestick-chart', 'figure'),
     Output('spread-chart', 'figure'),
     Output('volatility-chart', 'figure'),
     Output('last-update', 'children')],
    [Input('timeframe-dropdown', 'value'),
     Input('refresh-btn', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(timeframe, refresh_clicks, n_intervals):
    # Fetch data
    df = fetch_exchange_rates(timeframe)
    
    if df.empty:
        # Return empty components if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return (
            html.Div("No data available", className="text-center text-muted"),
            empty_fig, empty_fig, empty_fig, empty_fig,
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )