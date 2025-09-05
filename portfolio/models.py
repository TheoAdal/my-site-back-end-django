from django.db import models
from django.utils import timezone
import uuid

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # is_verified = models.BooleanField(default=False)
    # verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    # verification_token_expiry = models.DateTimeField(default=lambda: timezone.now() + timezone.timedelta(hours=1))
    
    def __str__(self):
        return self.username