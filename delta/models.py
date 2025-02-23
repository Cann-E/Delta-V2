from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('basicuser', 'Basic User'),
        ('admin', 'Administrator'),
        ('developer', 'Developer'),
        ('editor', 'Editor'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    status = models.BooleanField(default=True)



    def __str__(self):
        return self.username
