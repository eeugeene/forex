# ===== apps/core/models.py =====
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    business_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} - {self.business_name}"