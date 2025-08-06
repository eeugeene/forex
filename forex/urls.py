from django.urls import path
from . import views

# Define URL patterns for the forex application.
urlpatterns = [
    # Maps the root URL of the app to the 'index' view, which displays the main forex watcher dashboard.
    path('', views.index, name='index'),
    # Maps '/login/' to the custom login view, handling user authentication.
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # Maps '/logout/' to the custom logout view, handling user session termination.
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    # Maps '/api/forex-data/' to the forex_data view, providing real-time forex data via an API endpoint.
    path('api/forex-data/', views.forex_data, name='forex-data'),
]