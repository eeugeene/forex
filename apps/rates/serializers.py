from rest_framework import serializers
from .models import ExchangeRate

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['id', 'rate', 'buy_rate', 'sell_rate', 'timestamp', 'source']

# ===== apps/alerts/serializers.py =====
from rest_framework import serializers
from .models import Alert, AlertHistory

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'threshold_rate', 'alert_type', 'is_active', 'created_at']

class AlertHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertHistory
        fields = ['id', 'triggered_rate', 'triggered_at']