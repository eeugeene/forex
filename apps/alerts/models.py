# ===== apps/alerts/models.py =====
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Alert(models.Model):
    ALERT_TYPES = [
        ('above', 'Above Threshold'),
        ('below', 'Below Threshold'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    threshold_rate = models.DecimalField(max_digits=10, decimal_places=4)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.alert_type} {self.threshold_rate}"

class AlertHistory(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    triggered_rate = models.DecimalField(max_digits=10, decimal_places=4)
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-triggered_at']