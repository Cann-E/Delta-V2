from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.dispatch import receiver  # ✅ used to listen to signals
from django.db.models.signals import post_save  # ✅ fires when model is saved
from delta.pdf_utils import generate_pdf_for_request  # ✅ used to make PDF when approved

#  Custom user model that extends Django's default user
class CustomUser(AbstractUser):
    # override default groups and permissions
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )

    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='customuser_set',
        related_query_name='customuser',
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    # roles for the user
    ROLE_CHOICES = (
        ('basicuser', 'Basic User'),
        ('admin', 'Administrator'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='basicuser')
    status = models.BooleanField(default=True)
    uh_id = models.CharField(max_length=10, blank=True, null=True)  # UH ID field

    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)  # stores signature file
    is_active = models.BooleanField(default=True)  # check if user is active

    def __str__(self):
        return self.username  # shows username when printing user

    def is_admin(self):
        return self.role == 'admin'  # check if role is admin

    def can_change_request_status(self, request):
        return self.is_admin() or self == request.user  # only admin or owner can change status


#  This model represents a student request form
class Request(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')  # who submitted it
    request_type = models.CharField(max_length=20)  # type of request

    # basic form fields
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    # fields for major or address change
    current_major = models.CharField(max_length=100, blank=True, null=True)
    new_major = models.CharField(max_length=100, blank=True, null=True)
    old_address = models.CharField(max_length=255, blank=True, null=True)
    new_address = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')  # request status
    date_created = models.DateField(auto_now_add=True)  # auto-fill today's date
    pdf_file = models.FileField(upload_to='generated_pdfs/', blank=True, null=True)  # stores final PDF

    def save(self, *args, **kwargs):
        # fill in first and last name if missing
        if not self.first_name:
            self.first_name = self.user.first_name
        if not self.last_name:
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.request_type} ({self.status})"  # for admin view
