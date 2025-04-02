from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.dispatch import receiver  # ✅ Import receiver to handle signals
from django.db.models.signals import post_save  # ✅ Import post_save signal
from delta.pdf_utils import generate_pdf_for_request  # ✅ Import PDF generation function


class CustomUser(AbstractUser):
    # Override the inherited groups field
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )

    # Override the inherited user_permissions field
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    ROLE_CHOICES = (
        ('basicuser', 'Basic User'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    status = models.BooleanField(default=True)
    uh_id = models.CharField(max_length=10, blank=True, null=True)

    # NEW: Signature field for users
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == 'admin'

    def can_change_request_status(self, request):
        return self.is_admin() or self == request.user


class Request(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20)

    # ✅ Ensure these fields exist in your model
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    current_major = models.CharField(max_length=100, blank=True, null=True)
    new_major = models.CharField(max_length=100, blank=True, null=True)
    old_address = models.CharField(max_length=255, blank=True, null=True)
    new_address = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    date_created = models.DateField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='generated_pdfs/', blank=True, null=True)


    def save(self, *args, **kwargs):
        """ Auto-fill first_name and last_name from user session before saving """
        if not self.first_name:
            self.first_name = self.user.first_name
        if not self.last_name:
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.request_type} ({self.status})"

