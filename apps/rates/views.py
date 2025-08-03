# ===== apps/rates/views.py =====
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal
from .models import ExchangeRate
from .serializers import ExchangeRateSerializer

class ExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current exchange rate"""
        latest_rate = ExchangeRate.objects.first()
        if not latest_rate:
            # Generate mock data if none exists
            self.generate_mock_data()
            latest_rate = ExchangeRate.objects.first()
        
        serializer = self.get_serializer(latest_rate)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get historical rates with timeframe filter"""
        timeframe = request.query_params.get('timeframe', '7d')
        
        # Calculate date range
        now = timezone.now()
        if timeframe == '1d':
            start_date = now - timedelta(days=1)
        elif timeframe == '7d':
            start_date = now - timedelta(days=7)
        elif timeframe == '30d':
            start_date = now - timedelta(days=30)
        elif timeframe == '90d':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=7)
        
        rates = ExchangeRate.objects.filter(timestamp__gte=start_date)
        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_mock_data(self, request=None):
        """Generate mock exchange rate data"""
        base_rate = Decimal('3800.00')  # Base UGX/USD rate
        
        # Generate data for the last 30 days
        now = timezone.now()
        for i in range(30 * 24):  # Hourly data for 30 days
            timestamp = now - timedelta(hours=i)
            
            # Random variation around base rate
            variation = Decimal(str(random.uniform(-50, 50)))
            rate = base_rate + variation
            buy_rate = rate - Decimal('10.00')  # Spread
            sell_rate = rate + Decimal('10.00')
            
            ExchangeRate.objects.get_or_create(
                timestamp=timestamp,
                defaults={
                    'rate': rate,
                    'buy_rate': buy_rate,
                    'sell_rate': sell_rate,
                }
            )
        
        return Response({'message': 'Mock data generated successfully'})