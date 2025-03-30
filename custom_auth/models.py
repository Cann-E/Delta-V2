from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('basicuser', 'Basic User'),
        ('admin', 'Administrator'),
        ('developer', 'Developer'),
        ('editor', 'Editor'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    status = models.BooleanField(default=True)

    # Add related_name parameters to these fields
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        verbose_name='groups',
        related_name='custom_auth_customuser_set',
        help_text='The groups this user belongs to.',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        verbose_name='user permissions',
        related_name='custom_auth_customuser_permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username



# Create your models here.
