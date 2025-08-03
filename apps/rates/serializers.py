# ===== apps/rates/serializers.py =====
from rest_framework import serializers
from .models import ExchangeRate

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['id', 'rate', 'buy_rate', 'sell_rate', 'timestamp', 'source']

