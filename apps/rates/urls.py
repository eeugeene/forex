# ===== apps/rates/urls.py =====
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExchangeRateViewSet

router = DefaultRouter()
router.register(r'', ExchangeRateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]