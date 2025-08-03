from django.db import models
from django.utils import timezone

class ExchangeRate(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4)
    sell_rate = models.DecimalField(max_digits=10, decimal_places=4)
    timestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=50, default='mock_api')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"UGX/USD: {self.rate} at {self.timestamp}"