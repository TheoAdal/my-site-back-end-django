from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

from django.contrib.auth.models import AbstractUser

def default_expiry():
    return timezone.now() + timedelta(hours=1)

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    verification_token_expiry = models.DateTimeField(null=True, blank=True)
    reset_password_token = models.UUIDField(null=True, blank=True)
    reset_password_token_expiry = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        return self.username