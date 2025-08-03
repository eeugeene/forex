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
    
    # Calculate analytics
    analytics = calculate_analytics(df)
    
    # Create metrics cards
    metrics_cards = html.Div([
        html.Div([
            html.Div([
                html.Div("Current Rate", className="metric-label"),
                html.Div(f"UGX {analytics['current_rate']:.2f}", className="metric-value")
            ], className="metric-card")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.Div("24H Change", className="metric-label"),
                html.Div(f"{analytics['change']:+.2f}", 
                         className="metric-value",
                         style={'color': '#00d4aa' if analytics['change'] >= 0 else '#ff6b6b'})
            ], className="metric-card")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.Div("Change %", className="metric-label"),
                html.Div(f"{analytics['change_percent']:+.2f}%", 
                         className="metric-value",
                         style={'color': '#00d4aa' if analytics['change_percent'] >= 0 else '#ff6b6b'})
            ], className="metric-card")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.Div("High", className="metric-label"),
                html.Div(f"UGX {analytics['high']:.2f}", className="metric-value")
            ], className="metric-card")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.Div("Low", className="metric-label"),
                html.Div(f"UGX {analytics['low']:.2f}", className="metric-value")
            ], className="metric-card")
        ], className="col-md-2"),
        
        html.Div([
            html.Div([
                html.Div("Volatility", className="metric-label"),
                html.Div(f"{analytics['volatility']:.2f}", className="metric-value")
            ], className="metric-card")
        ], className="col-md-2")
    ], className="row")
    
    # Create rate trend chart
    rate_chart = go.Figure()
    
    rate_chart.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['rate'],
        mode='lines+markers',
        name='Exchange Rate',
        line=dict(color='#00d4aa', width=2),
        marker=dict(size=4),
        hovertemplate='<b>Rate</b>: UGX %{y:.2f}<br><b>Time</b>: %{x}<extra></extra>'
    ))
    
    # Add moving average
    if len(df) >= 7:
        df['ma_7'] = df['rate'].rolling(window=7).mean()
        rate_chart.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ma_7'],
            mode='lines',
            name='7-Day Moving Average',
            line=dict(color='#3861fb', width=1, dash='dash'),
            hovertemplate='<b>7-Day MA</b>: UGX %{y:.2f}<br><b>Time</b>: %{x}<extra></extra>'
        ))
    
    rate_chart.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="UGX/USD Exchange Rate", font=dict(color='#f0f0f0')),
        xaxis=dict(title="Time", color='#848e9c'),
        yaxis=dict(title="Rate (UGX)", color='#848e9c'),
        legend=dict(font=dict(color='#f0f0f0')),
        hovermode='x unified'
    )
    
    # Create candlestick chart (simulated OHLC from rate data)
    candlestick_chart = create_candlestick_chart(df)
    
    # Create spread analysis chart
    spread_chart = go.Figure()
    
    spread_chart.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['buy_rate'],
        mode='lines',
        name='Buy Rate',
        line=dict(color='#00d4aa', width=2),
        hovertemplate='<b>Buy Rate</b>: UGX %{y:.2f}<br><b>Time</b>: %{x}<extra></extra>'
    ))
    
    spread_chart.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['sell_rate'],
        mode='lines',
        name='Sell Rate',
        line=dict(color='#ff6b6b', width=2),
        hovertemplate='<b>Sell Rate</b>: UGX %{y:.2f}<br><b>Time</b>: %{x}<extra></extra>'
    ))
    
    # Fill between buy and sell rates
    spread_chart.add_trace(go.Scatter(
        x=df['timestamp'].tolist() + df['timestamp'].tolist()[::-1],
        y=df['buy_rate'].tolist() + df['sell_rate'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255, 107, 107, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Spread',
        hoverinfo='skip'
    ))
    
    spread_chart.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="Buy/Sell Rate Spread", font=dict(color='#f0f0f0')),
        xaxis=dict(title="Time", color='#848e9c'),
        yaxis=dict(title="Rate (UGX)", color='#848e9c'),
        legend=dict(font=dict(color='#f0f0f0')),
        hovermode='x unified'
    )
    
    # Create volatility chart
    volatility_chart = create_volatility_chart(df)
    
    last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return metrics_cards, rate_chart, candlestick_chart, spread_chart, volatility_chart, last_update

def create_candlestick_chart(df):
    """Create candlestick chart from rate data"""
    if len(df) < 4:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title="Insufficient data for candlestick chart"
        )
        return fig
    
    # Group data by day to create OHLC
    df['date'] = df['timestamp'].dt.date
    daily_data = df.groupby('date').agg({
        'rate': ['first', 'max', 'min', 'last'],
        'timestamp': 'first'
    }).round(2)
    
    daily_data.columns = ['open', 'high', 'low', 'close', 'timestamp']
    daily_data = daily_data.reset_index()
    
    fig = go.Figure(data=go.Candlestick(
        x=daily_data['timestamp'],
        open=daily_data['open'],
        high=daily_data['high'],
        low=daily_data['low'],
        close=daily_data['close'],
        increasing_line_color='#00d4aa',
        decreasing_line_color='#ff6b6b',
        hovertemplate='''
        <b>Date</b>: %{x}<br>
        <b>Open</b>: UGX %{open:.2f}<br>
        <b>High</b>: UGX %{high:.2f}<br>
        <b>Low</b>: UGX %{low:.2f}<br>
        <b>Close</b>: UGX %{close:.2f}<br>
        <extra></extra>
        '''
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="Daily OHLC Candlestick Chart", font=dict(color='#f0f0f0')),
        xaxis=dict(title="Date", color='#848e9c'),
        yaxis=dict(title="Rate (UGX)", color='#848e9c'),
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_volatility_chart(df):
    """Create volatility analysis chart"""
    if len(df) < 10:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title="Insufficient data for volatility analysis"
        )
        return fig
    
    # Calculate rolling volatility (standard deviation)
    window = min(7, len(df) // 2)
    df['volatility'] = df['rate'].rolling(window=window).std()
    
    # Calculate price changes
    df['price_change'] = df['rate'].pct_change() * 100
    
    # Create subplot with volatility and price changes
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Rolling Volatility', 'Price Changes (%)'),
        vertical_spacing=0.1
    )
    
    # Volatility chart
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['volatility'],
            mode='lines+markers',
            name='Volatility',
            line=dict(color='#3861fb', width=2),
            marker=dict(size=3),
            hovertemplate='<b>Volatility</b>: %{y:.3f}<br><b>Time</b>: %{x}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Price changes chart
    colors = ['#00d4aa' if x >= 0 else '#ff6b6b' for x in df['price_change'].fillna(0)]
    
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['price_change'],
            name='Price Change %',
            marker_color=colors,
            hovertemplate='<b>Change</b>: %{y:.2f}%<br><b>Time</b>: %{x}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text="Volatility Analysis", font=dict(color='#f0f0f0')),
        showlegend=False,
        height=600
    )
    
    fig.update_xaxes(title_text="Time", color='#848e9c')
    fig.update_yaxes(title_text="Volatility", color='#848e9c', row=1, col=1)
    fig.update_yaxes(title_text="Change (%)", color='#848e9c', row=2, col=1)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8050)
