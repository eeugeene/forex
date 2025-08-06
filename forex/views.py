from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.core.cache import cache
import yfinance as yf

# CustomLoginView handles user login, rendering the 'login.html' template.
class CustomLoginView(LoginView):
    template_name = 'login.html'

# CustomLogoutView handles user logout, redirecting to the 'login' page after successful logout.
class CustomLogoutView(LogoutView):
    next_page = 'login'

# The index view requires a logged-in user to access.
# It renders the main 'index.html' template, which displays the forex watcher.
@login_required
def index(request):
    return render(request, 'index.html')

# forex_data view provides real-time forex exchange rate data as a JSON response.
# It fetches data from yfinance and caches it for 60 seconds to reduce API calls.
def forex_data(request):
    # Attempt to retrieve cached forex data.
    data = cache.get('forex_data')
    
    # If data is not in cache, fetch it from yfinance.
    if not data:
        # Initialize yfinance Ticker objects for UGX/USD and USD/UGX.
        ugxusd_data = yf.Ticker("UGXUSD=X")
        usdugx_data = yf.Ticker("USDUGX=X")

        # Fetch historical data for the last day at 1-minute intervals.
        ugxusd_history = ugxusd_data.history(period="1d", interval="1m")
        usdugx_history = usdugx_data.history(period="1d", interval="1m")

        # Get the latest (most recent) data point from the historical data.
        ugxusd_latest = ugxusd_history.iloc[-1]
        usdugx_latest = usdugx_history.iloc[-1]

        # Structure the fetched data into a dictionary for easy access in the frontend.
        data = {
            'ugxusd': {
                'exchange_rate': ugxusd_latest['Close'],  # Current exchange rate
                'buy_rate': ugxusd_latest['Open'],       # Buy rate (using Open price as a proxy)
                'sell_rate': ugxusd_latest['Close'],     # Sell rate (using Close price as a proxy)
                'high': ugxusd_history['High'].max(),    # 24-hour high
                'low': ugxusd_history['Low'].min(),      # 24-hour low
            },
            'usdugx': {
                'exchange_rate': usdugx_latest['Close'],
                'buy_rate': usdugx_latest['Open'],
                'sell_rate': usdugx_latest['Close'],
                'high': usdugx_history['High'].max(),
                'low': usdugx_history['Low'].min(),
            }
        }
        # Cache the fetched data for 60 seconds to avoid frequent API calls.
        cache.set('forex_data', data, 60)
    
    # Return the forex data as a JSON response.
    return JsonResponse(data)
