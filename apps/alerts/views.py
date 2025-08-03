# ===== apps/alerts/views.py =====
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Alert, AlertHistory
from .serializers import AlertSerializer, AlertHistorySerializer

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    
    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get alert history for the user"""
        user_alerts = Alert.objects.filter(user=request.user)
        history = AlertHistory.objects.filter(alert__in=user_alerts)
        serializer = AlertHistorySerializer(history, many=True)
        return Response(serializer.data)
